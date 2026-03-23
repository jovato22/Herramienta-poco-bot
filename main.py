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
    """Calcula el múltiplo anterior y el siguiente de 144."""
    prev_m = (current_n // 144) * 144
    # Si el número actual ya es múltiplo, el anterior real sería -144
    if prev_m == current_n:
        prev_m = current_n - 144
        
    next_m = ((current_n // 144) + 1) * 144
    return prev_m, next_m

async def bloque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: `/bloque <numero>`", parse_mode="Markdown")
        return

    try:
        n = int(context.args[0])
    except:
        await update.message.reply_text("❌ Número no válido.")
        return

    await update.message.reply_chat_action("typing")

    # 1. Obtener datos Bloque solicitado (N)
    data_n = get_block_data(n)
    if not data_n:
        await update.message.reply_text(f"⏳ El bloque {n} no existe o no hay datos.")
        return

    # 2. Obtener datos Múltiplo 144 Anterior (Automático)
    prev_144_height, next_144_height = get_144_stats(n)
    data_prev = get_block_data(prev_144_height)

    # 3. Obtener datos Bloque N+6
    data_n6 = get_block_data(n + 6)

    # --- CONSTRUCCIÓN DEL MENSAJE ---
    msg = f"🔍 **ANÁLISIS DE RED (Bloque {n})**\n\n"

    # Sección Múltiplo Anterior
    if data_prev and data_n['price']:
        sym_prev = "🔼" if data_n['price'] > data_prev['price'] else "🔽"
        diff_prev = data_n['price'] - data_prev['price']
        msg += f"⏪ **Último Múltiplo 144 ({prev_144_height})**\n"
        msg += f"💰 Precio entonces: `${data_prev['price']:,.2f}`\n"
        msg += f"📊 Variación hasta N: `{'+' if diff_prev > 0 else ''}{diff_prev:,.2f} USD` {sym_prev}\n\n"

    # Sección Bloque Solicitado
    msg += f"🟦 **BLOQUE {n} (Tu consulta)**\n"
    msg += f"💰 Precio: `${data_n['price']:,.2f} USD`\n"
    msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n, 144) else '❌'}\n\n"

    # Sección N+6
    if data_n6:
        sym6 = "✔️" if data_n6['price'] > data_n['price'] else "❌"
        diff6 = data_n6['price'] - data_n['price']
        msg += f"🟩 **BLOQUE {n+6} (Confirmación)**\n"
        msg += f"💰 Precio: `${data_n6['price']:,.2f} USD` {sym6}\n"
        msg += f"📈 Variación: `{'+' if diff6 > 0 else ''}{diff6:,.2f} USD` \n\n"

    # Sección Próximo Objetivo
    faltan = next_144_height - n
    msg += f"🎯 **Próximo Múltiplo 144:**\n"
    msg += f"➡️ Bloque: `{next_144_height}` (Faltan: `{faltan}`)"

    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("bloque", bloque))
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Bot Listo.")))
    application.run_polling()

if __name__ == "__main__":
    main()
