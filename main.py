import fnmatch
from json.decoder import JSONDecodeError
from discord.ext import tasks
from commands import *

config = dotenv_values(".env")
client = discord.Client()
price_channel_ids = config["PRICE_CHANNELS"].split(",")
price_channels = []


@client.event
async def on_ready():
    print('### CATE Bot logged in as {0.user} ###'.format(client))
    for channel_id in price_channel_ids:
        channel = client.get_channel(int(channel_id))
        if channel is not None:
            price_channels.append(channel)
    print('Found %s price channel(s).' % len(price_channels))
    task_update_price_channel.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Command: btc
    #
    # Display a BTC/USDT chart.
    if message.content.lower() == 'btc' or fnmatch.fnmatch(message.content.lower(), "btc:*"):
        interval = "1h"
        if fnmatch.fnmatch(message.content.lower(), "btc:*"):
            interval = message.content.lower().replace("btc:", "")
            if interval not in ["1m", "3m", "5m", "15m", "30m", "45m", "1h", "2h", "3h", "4h", "1d", "1w"]:
                await message.channel.send("Invalid timeframe.\nAllowed timeframes are: "
                                           "1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 3h, 4h, 1d, 1w")
                return
        await display_chart(ctx=message.channel, interval=interval)

    # Command: p
    #
    # Display price data for token.
    if message.content.lower() == 'p':
        await display_price(message.channel)

    # Command: chart
    #
    # Display a link to a candle chart for the token.
    if message.content.lower() == 'chart':
        await display_chart_link(message.channel)

    # Command: contract
    #
    # Display the contract address of the token.
    if message.content.lower() == 'contract':
        await display_contract(message.channel)

    # Command: buy
    #
    # Display a link to a exchange where you can buy the token.
    if message.content.lower() == 'buy':
        await display_buy(message.channel)

    # Command: test_p
    #
    # Development version of the p command.
    if message.content.lower() == 'test_p':
        await test_display_price(message.channel)


async def update_price_channel():
    for channel in price_channels:
        if channel is not None:
            price_request = get_price(config["TOKEN_ADDRESS"])
            try:
                print("update_price_channel: " + price_request['message'])
                return
            except KeyError:
                token_usd_price = native_to_usd_price(price_request["nativePrice"]["value"])
                formatted_price = '{:.10f}'.format(token_usd_price).replace('.', '‸')
                print(formatted_price)
                await rename_channel(channel, formatted_price)
                # await display_price(channel)


"""
Tasks
"""


@tasks.loop(seconds=300)
async def task_update_price_channel():
    if len(price_channels) > 0:
        print("updating price channel...")
        try:
            await update_price_channel()
        except JSONDecodeError:
            print("error while trying to update price channel")
        else:
            print("done.")


client.run(config["BOT_KEY"])
