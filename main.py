import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURACIÓN ---
TOKEN = "8725996090:AAF44XD_l4TpymdFrEareVG-RpYH_OM8kzg"

def get_block_data(height):
    """Obtiene hash, timestamp y precio estimado del bloque."""
    try:
        # 1. Obtener Hash del bloque
        hash_res = requests.get(f"https://mempool.space/api/block-height/{height}")
        if hash_res.status_code != 200: return None
        block_hash = hash_res.text
        
        # 2. Obtener datos detallados del bloque (timestamp)
        block_data = requests.get(f"https://mempool.space/api/block/{block_hash}").json()
        timestamp = block_data['timestamp']
        
        # 3. Obtener precio histórico (Usamos la API de CoinGecko o similar)
        # Para esta prueba, consultamos un precio de referencia basado en el tiempo
        # Nota: Las APIs de precio histórico real a veces son lentas o de pago, 
        # aquí usamos una estimación para la comparativa:
        price_res = requests.get(f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={timestamp}&to={timestamp+3600}").json()
        price = price_res['prices'][0][1] if 'prices' in price_res else None
        
        return {"price": price, "timestamp": timestamp}
    except:
        return None

def is_multiple(n, base):
    return n % base == 0

async def bloque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        n = int(context.args[0])
    except:
        await update.message.reply_text("❌ Uso: /bloque <numero>")
        return

    await update.message.reply_chat_action("typing")

    # Datos Bloque N
    data_n = get_block_data(n)
    if not data_n:
        await update.message.reply_text(f"⏳ El bloque {n} no existe o no hay datos.")
        return

    # Datos Bloque N+6
    n6 = n + 6
    data_n6 = get_block_data(n6)

    # Lógica de comparación
    msg = f"🟦 **BLOQUE {n}**\n"
    msg += f"💰 Precio: `${data_n['price']:,.2f} USD`\n"
    msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n, 144) else '❌'}\n\n"

    if data_n6:
        # COMPARACIÓN REAL
        symbol6 = "✔️" if data_n6['price'] > data_n['price'] else "❌"
        msg += f"🟩 **BLOQUE {n6} (N+6)**\n"
        msg += f"💰 Precio: `${data_n6['price']:,.2f} USD` {symbol6}\n"
        msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n6, 144) else '❌'}\n"
        
        diff = data_n6['price'] - data_n['price']
        msg += f"\n📈 Variación: `{'+' if diff > 0 else ''}{diff:,.2f} USD`"
    else:
        msg += f"🟩 **BLOQUE {n6}**\n⏳ Aún no minado o sin datos de precio."

    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("bloque", bloque))
    app.run_polling()

if __name__ == "__main__":
    main()
