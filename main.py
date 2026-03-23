import requests
from telegram.ext import Updater, CommandHandler

API_PRICE = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
API_BLOCK = "https://mempool.space/api/block-height/{}"
API_HEIGHT = "https://mempool.space/api/blocks/tip/height"

def get_price():
    r = requests.get(API_PRICE).json()
    return r["bitcoin"]["usd"]

def get_block_height():
    return requests.get(API_HEIGHT).json()

def get_block_time(height):
    try:
        data = requests.get(API_BLOCK.format(height)).json()
        return data["timestamp"]
    except:
        return None

def is_multiple(n, base):
    return n % base == 0

def bloque(update, context):
    try:
        n = int(context.args[0])
    except:
        update.message.reply_text("Uso: /bloque <numero>")
        return

    current_height = get_block_height()

    # Bloque principal
    block_time = get_block_time(n)
    if block_time is None:
        update.message.reply_text(f"Bloque {n} aún no está minado. Te avisaré cuando llegue.")
        return

    price_now = get_price()
    price_prev = get_price()

    symbol = "➖"
    if price_now > price_prev:
        symbol = "✔️"
    elif price_now < price_prev:
        symbol = "❌"

    msg = f"🟦 Bloque {n}\n"
    msg += f"Precio BTC: {price_now} USD {symbol}\n"
    msg += f"Múltiplo de 144: {'✔️' if is_multiple(n,144) else '❌'}\n"
    msg += f"Múltiplo de 2016: {'✔️' if is_multiple(n,2016) else '❌'}\n\n"

    # Bloque + 6
    n6 = n + 6
    block_time6 = get_block_time(n6)

    if block_time6:
        price6 = get_price()
        price5 = get_price()

        symbol6 = "➖"
        if price6 > price5:
            symbol6 = "✔️"
        elif price6 < price5:
            symbol6 = "❌"

        msg += f"🟩 Bloque {n6} (bloque + 6)\n"
        msg += f"Precio BTC: {price6} USD {symbol6}\n"
        msg += f"Múltiplo de 144: {'✔️' if is_multiple(n6,144) else '❌'}\n"
        msg += f"Múltiplo de 2016: {'✔️' if is_multiple(n6,2016) else '❌'}\n"

    update.message.reply_text(msg)

def main():
    updater = Updater("BOT_TOKEN_AQUI", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("bloque", bloque))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()