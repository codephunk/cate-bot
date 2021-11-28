import discord
from blockchain import *
from dotenv import dotenv_values
config = dotenv_values(".env")


async def display_price(ctx):
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


async def test_display_price(ctx):
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


async def display_buy(ctx):
    embed = discord.Embed(title="Buy %s on PancakeSwap" % config["TOKEN_SYMBOL"],
                          url=config["BUY_URL"],
                          color=discord.Color.orange())
    await ctx.send(embed=embed)


async def display_chart(ctx, symbol="BINANCE:BTCUSDT", height="300", interval="1h"):
    chart_image_url = "https://api.chart-img.com/v1/tradingview/advanced-chart?interval=%s&height=%s&symbol=%s" \
                      % (interval, height, symbol)
    embed = discord.Embed(color=discord.Color.orange()).set_image(url=chart_image_url)
    await ctx.send(embed=embed)


async def display_chart_link(ctx):
    embed = discord.Embed(title="%s/USD Chart" % config["TOKEN_SYMBOL"],
                          url=config["CHART_URL"],
                          color=discord.Color.orange())
    await ctx.send(embed=embed)


async def display_contract(ctx):
    embed = discord.Embed(title="%s Contract Address" % config["TOKEN_SYMBOL"],
                          description=config["TOKEN_ADDRESS"],
                          color=discord.Color.orange())
    await ctx.send(embed=embed)


async def rename_channel(channel, new_name):
    await channel.edit(name=new_name)
