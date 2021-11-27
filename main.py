import discord
from discord.ext import tasks
from blockchain import *

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

    """
    Command: p
    
    Display price data for token.
    """
    if message.content.lower() == 'p':
        ctx = message.channel
        price_request_7 = get_price_x_days_ago(config["TOKEN_ADDRESS"], 7)
        price_request_30 = get_price_x_days_ago(config["TOKEN_ADDRESS"], 30)
        price_request = get_price(config["TOKEN_ADDRESS"])
        native_price_request = get_price('0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')
        try:
            print("today: " + price_request['message'])
            print("5D: " + price_request_7['message'])
            print("30D: " + price_request_30['message'])
            print("BNB: " + native_price_request["usdPrice"])
            await ctx.send(price_request['message'])
            return
        except KeyError:
            native_price_usd = native_price_request["usdPrice"]
            token_wbnb_price = int(price_request["nativePrice"]["value"]) / (10 ** 18)
            token_usd_price = token_wbnb_price * native_price_usd
            movement_percent_7 = get_movement_percent(token_usd_price, price_request_7["usdPrice"])
            movement_percent_30 = get_movement_percent(token_usd_price, price_request_30["usdPrice"])
            price_usd = '{:.10f}'.format(token_usd_price) + ' USD'
            embed = discord.Embed(title=price_usd,
                                  color=discord.Color.orange())
            embed.add_field(name="**{:.2f}%**".format(movement_percent_7), value="7-day", inline=True)
            embed.add_field(name="**{:.2f}%**".format(movement_percent_30), value="30-day", inline=True)
            embed.set_author(name=config["TOKEN_SYMBOL"], url=config["TOKEN_URL"], icon_url=config["TOKEN_IMAGE"])
            embed.set_footer(text="via %s" % price_request["exchangeName"])
            await ctx.send(embed=embed)

    """
    Command: chart

    Display a link to a candle chart for the token.
    """
    if message.content.lower() == 'chart':
        ctx = message.channel
        embed = discord.Embed(title="%s/USD Chart" % config["TOKEN_SYMBOL"],
                              url=config["CHART_URL"],
                              color=discord.Color.orange())
        await ctx.send(embed=embed)

    """
    Command: contract

    Display the contract address of the token.
    """
    if message.content == 'contract' or message.content == 'Contract':
        ctx = message.channel
        embed = discord.Embed(title="%s Contract Address" % config["TOKEN_SYMBOL"],
                              description=config["TOKEN_ADDRESS"],
                              color=discord.Color.orange())
        await ctx.send(embed=embed)

    """
    Command: buy

    Display a link to a exchange where you can buy the token.
    """
    if message.content.lower() == 'buy':
        ctx = message.channel
        embed = discord.Embed(title="Buy %s on PancakeSwap" % config["TOKEN_SYMBOL"],
                              url=config["BUY_URL"],
                              color=discord.Color.orange())
        await ctx.send(embed=embed)

    """
    Command: test_p

    Development version of the p command.
    """
    if message.content.lower() == 'test_p':
        ctx = message.channel
        price_request_7 = get_price_x_days_ago(config["TOKEN_ADDRESS"], 7)
        price_request_30 = get_price_x_days_ago(config["TOKEN_ADDRESS"], 30)
        price_request = get_price(config["TOKEN_ADDRESS"])
        try:
            print("today: " + price_request['message'])
            print("5D: " + price_request_7['message'])
            print("30D: " + price_request_30['message'])
            await ctx.send(price_request['message'])
            return
        except KeyError:
            token_usd_price = native_to_usd_price(price_request["nativePrice"]["value"])
            movement_percent_7 = get_movement_percent(token_usd_price, price_request_7["usdPrice"])
            movement_percent_30 = get_movement_percent(token_usd_price, price_request_30["usdPrice"])
            price_usd = '{:.10f}'.format(token_usd_price) + ' USD'
            embed = discord.Embed(title=price_usd, color=discord.Color.orange())
            embed.add_field(name="**{:.2f}%**".format(movement_percent_7), value="7-day", inline=True)
            embed.add_field(name="**{:.2f}%**".format(movement_percent_30), value="30-day", inline=True)
            embed.set_author(name=config["TOKEN_SYMBOL"], url=config["TOKEN_URL"], icon_url=config["TOKEN_IMAGE"])
            embed.set_footer(text="via %s" % price_request["exchangeName"])
            await ctx.send(embed=embed)


async def rename_channel(channel, new_name):
    await channel.edit(name=new_name)


def update_price_channel():
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
                return rename_channel(channel, formatted_price)


"""
Tasks
"""


@tasks.loop(seconds=300)
async def task_update_price_channel():
    if len(price_channels) > 0:
        print("updating price channel...")
        await update_price_channel()
        print("done.")


client.run(config["BOT_KEY"])
