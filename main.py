import requests
from telegram.ext import Updater, CommandHandler

API_PRICE = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

def start(update, context):
    update.message.reply_text("Bot operativo. Usa /bloque <numero>")

# Obtener hash del bloque desde la altura
def get_block_hash(height):
    try:
        return requests.get(f"https://mempool.space/api/block-height/{height}").text
    except:
        return None

# Obtener timestamp del bloque usando el hash
def get_block_time(height):
    block_hash = get_block_hash(height)
    if not block_hash:
        return None
    try:
        data = requests.get(f"https://mempool.space/api/block/{block_hash}").json()
        return data["timestamp"]
    except:
        return None

# Precio BTC
def get_price():
    try:
        r = requests.get(API_PRICE).json()
        return r["bitcoin"]["usd"]
    except:
        return None

# Múltiplos
def is_multiple(n, base):
    return n % base == 0

def bloque(update, context):
    try:
        n = int(context.args[0])
    except:
        update.message.reply_text("Uso: /bloque <numero>")
        return

    block_time = get_block_time(n)
    if block_time is None:
        update.message.reply_text(f"Bloque {n} aún no está minado.")
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
    updater = Updater("8725996090:AAF44XD_l4TpymdFrEareVG-RpYH_OM8kzg", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("bloque", bloque))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()