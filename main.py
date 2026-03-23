import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURACIÓN ---
TOKEN = "8725996090:AAF44XD_l4TpymdFrEareVG-RpYH_OM8kzg"

def get_block_data(height):
    """Obtiene hash, timestamp y precio histórico del bloque."""
    try:
        # 1. Obtener Hash
        hash_res = requests.get(f"https://mempool.space/api/block-height/{height}")
        if hash_res.status_code != 200: return None
        block_hash = hash_res.text
        
        # 2. Obtener datos del bloque
        block_data = requests.get(f"https://mempool.space/api/block/{block_hash}").json()
        timestamp = block_data['timestamp']
        
        # 3. Obtener precio histórico (CoinGecko)
        price_url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={timestamp}&to={timestamp+3600}"
        price_res = requests.get(price_url).json()
        
        price = price_res['prices'][0][1] if 'prices' in price_res and len(price_res['prices']) > 0 else None
        
        return {"price": price, "height": height}
    except:
        return None

def is_multiple(n, base):
    return n % base == 0

def get_144_stats(current_n):
    prev_m = (current_n // 144) * 144
    if prev_m == current_n:
        prev_m = current_n - 144
    next_m = ((current_n // 144) + 1) * 144
    return prev_m, next_m

async def bloque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: `/bloque <numero>`")
        return

    try:
        n = int(context.args[0])
    except:
        await update.message.reply_text("❌ Número no válido.")
        return

    await update.message.reply_chat_action("typing")

    # Obtener datos
    data_n = get_block_data(n)
    if not data_n:
        await update.message.reply_text(f"⏳ El bloque {n} no existe o no hay datos.")
        return

    prev_144_h, next_144_h = get_144_stats(n)
    data_prev = get_block_data(prev_144_h)
    
    n6 = n + 6
    data_n6 = get_block_data(n6)

    # --- CONSTRUCCIÓN DEL MENSAJE ---
    msg = f"🔍 **ANÁLISIS DE RED (Bloque {n})**\n\n"

    # 1. Múltiplo Anterior
    if data_prev and data_n['price']:
        diff_prev = data_n['price'] - data_prev['price']
        sym_prev = "🔼" if diff_prev > 0 else "🔽"
        msg += f"⏪ **Último Múltiplo 144 ({prev_144_h})**\n"
        msg += f"💰 Precio: `${data_prev['price']:,.2f}`\n"
        msg += f"📊 Variación hasta N: `{'+' if diff_prev > 0 else ''}{diff_prev:,.2f} USD` {sym_prev}\n\n"

    # 2. Bloque Solicitado
    msg += f"🟦 **BLOQUE {n}**\n"
    msg += f"💰 Precio: `${data_n['price']:,.2f} USD`\n"
    msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n, 144) else '❌'}\n\n"

    # 3. Bloque N+6
    msg += f"🟩 **BLOQUE {n6} (N+6)**\n"
    if data_n6:
        diff6 = data_n6['price'] - data_n['price']
        sym6 = "✔️" if data_n6['price'] > data_n['price'] else "❌"
        msg += f"💰 Precio: `${data_n6['price']:,.2f} USD` {sym6}\n"
        msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n6, 144) else '❌'}\n"
        msg += f"📈 Variación: `{'+' if diff6 > 0 else ''}{diff6:,.2f} USD` \n\n"
    else:
        msg += f"✅ Confirmado\n"
        msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n6, 144) else '❌'}\n"
        msg += f"⏳ Esperando datos de precio...\n\n"

    # 4. Próximo Objetivo (CON HORAS)
    faltan = next_144_h - n
    horas_aprox = (faltan * 10) / 60
    msg += f"🎯 **Próximo Múltiplo 144:**\n"
    msg += f"➡️ Bloque: `{next_144_h}`\n"
    msg += f"⌛ Faltan: `{faltan}` bloques (aprox. {horas_aprox:.1f} horas)"

    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("bloque", bloque))
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Bot Activo.")))
    application.run_polling()

if __name__ == "__main__":
    main()
