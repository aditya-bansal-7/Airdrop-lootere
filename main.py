import telebot 
import os
import requests
import json

TOKEN =  os.getenv('TOKEN')

CMCAPIKEY = "2748b8f5-8e99-4210-845d-78176b3a1f62"

bot = telebot.TeleBot(TOKEN)

def get_price(crypto_symbol, currency):
    """Get the price of a cryptocurrency in a given currency."""
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={crypto_symbol}&convert={currency}'
    headers = {'X-CMC_PRO_API_KEY': CMCAPIKEY}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if 'status' in data and data['status']['error_code'] == 400:
            return None
        name = data['data'][(crypto_symbol).upper()]['name']
        slug = data['data'][(crypto_symbol).upper()]['slug']
        price = data['data'][(crypto_symbol).upper()]['quote'][currency.upper()]['price']
        percent_change_24h = data['data'][crypto_symbol.upper()]['quote'][currency.upper()]['percent_change_24h']
        return slug, name, price, percent_change_24h
    except KeyError:
        return None

# handle inline callback 
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'deleta':
        bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['start'])
def start(message):
    msg_txt = '''This bot recognizes numbers and currencies in the text and then automatically sends a message in which the amount is converted to other currencies. The price is taken from <a href="https://www.coingecko.com/">CoinGecko</a>.
By example
>>>5 trx
5 <a herf='https://www.coingecko.com/en/coins/tron' >TRON</a> (trx):
0.347 usd      
20.93 rub
(The bot translated the price into rubles and dollars)

>>>1 btc
<a herf='https://www.coingecko.com/en/coins/bitcoin' >Bitcoin</a> (btc):
23,286 usd      | -4.64%
1,404,500 rub   | -4.64%
(In this case, the percentage difference from the previous day is also shown)

>>>1 uah
Ukrainian Hryvnia (uah):
0.027,076 usd   | -0.00%
1.633,1 rub     | -0.00%
(all national currencies are also supported. Data is taken from CBRF rates (https://www.cbr.ru/currency_base/daily/))

Commands
/start or /help -this
/settings - you can change the main chat currencies. You can choose from all the classic currencies and several popular cryptocurrencies (by default there are usd and rub).  
/c или /charts - shows the graph for the selected cryptocurrency. Supports 1 day / 5 day / 1 month / 6 month time frames. Source - Mexc (https://www.mexc.com/)

The bot also works great in channel comments and individual chats!

Newly added futures
Calculator
>>> (15+4.6)*0.25
=4.9

Floor and basic information about the CoralCube (https://coralcube.io/) collection
>>> !abc_abracadabra
ABC
 (https://magiceden.io/marketplace/abc_abracadabra)23.8 SOL ≈ 688.29 USDT
489 listed (4%) | Royalty -  0%
Coralcube
 (https://coralcube.io/collection/abc_abracadabra)Discord (https://discord.gg/ABCCommunity) | Twitter (https://twitter.com/ABC123Community)

And Opensea (https://opensea.io/) collection
>>> !valhalla
Valhalla
 (https://opensea.io/collection/valhalla)1.1299 ETH ≈ 1491.87 USDT
1360 listed (15%) | Royalty -  5%
Discord (https://discord.gg/joinvalhalla) | Twitter (https://twitter.com/valhalla) | website (http://joinvalhalla.com/)

Donate me pls т-т
BSC/ETH: 0x091Bc244bd50A3BdF45a14f6636e14fD1CDeDD8F
SOL: HG1Jvw1UBKtjvqHvs97beFrLScz4xRAvyxZispSM3nXM

Admin - @supchikawai'''
    bot.reply_to(message,  msg_txt)


@bot.message_handler(func=lambda message: True)
def handle_message(message):

    msg_arr = message.text.split()

    if len(msg_arr) == 2 or len(msg_arr) == 3:
        if(msg_arr[0].isdigit()):
            try:
                name,slug, price , percent_change_24h = get_price(msg_arr[1], "usd")
                if len(msg_arr) == 3:
                    name,slug, price_new , percent_change_24h_new = get_price(msg_arr[1], msg_arr[2])
                if price is not None:
                    msg_txt = f'<code>{name} ({msg_arr[1]}):\n{(price * int(msg_arr[0])):.4f} usd \t\t| {percent_change_24h:.2f}% </code>'
                    # for inr currency
                    if len(msg_arr) == 3:
                        if msg_arr[2] == "inr" and msg_arr[1] == "usdt":
                            price_new = price_new + 4
                        msg_txt += f'<code>\n{(price_new * int(msg_arr[0])):.2f} {msg_arr[2]}</code>'

                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(text="Delete", callback_data="deleta"))
                    markup.add(telebot.types.InlineKeyboardButton(text=name.capitalize(), url="https://coinmarketcap.com/currencies/" + slug))
                    bot.reply_to(message, text=msg_txt,reply_markup=markup, parse_mode="HTML")
                    return
            except Exception as e:
                print(e)
                pass

    # calculator 
    try:
        result = eval(message.text)
        if result is not None:
            bot.reply_to(message, result)
            return
    except:
        pass


if __name__ == "__main__":
    bot.polling(none_stop=True)