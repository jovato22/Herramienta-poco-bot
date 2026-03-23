import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURACIÓN ---
# Token de prueba (Recuerda revocarlo si vas a usarlo en serio más adelante)
TOKEN = "8725996090:AAF44XD_l4TpymdFrEareVG-RpYH_OM8kzg"

def get_block_data(height):
    """Obtiene hash, timestamp y precio histórico del bloque usando Mempool y CoinGecko."""
    try:
        # 1. Obtener Hash del bloque desde la altura
        hash_res = requests.get(f"https://mempool.space/api/block-height/{height}")
        if hash_res.status_code != 200: return None
        block_hash = hash_res.text
        
        # 2. Obtener datos del bloque (timestamp)
        block_data = requests.get(f"https://mempool.space/api/block/{block_hash}").json()
        timestamp = block_data['timestamp']
        
        # 3. Obtener precio histórico exacto en ese timestamp
        # Consultamos un rango de 1 hora para asegurar que CoinGecko devuelva el punto de datos
        price_url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={timestamp}&to={timestamp+3600}"
        price_res = requests.get(price_url).json()
        
        price = price_res['prices'][0][1] if 'prices' in price_res and len(price_res['prices']) > 0 else None
        
        return {"price": price, "timestamp": timestamp}
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        return None

def is_multiple(n, base):
    return n % base == 0

def get_next_144_multiple(current_n):
    """Calcula el próximo múltiplo de 144 y cuántos bloques faltan."""
    next_m = ((current_n // 144) + 1) * 144
    remaining = next_m - current_n
    return next_m, remaining

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot Bitcoin Operativo.\nUsa `/bloque <numero>` para analizar la red.", parse_mode="Markdown")

async def bloque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: `/bloque 845000`", parse_mode="Markdown")
        return

    try:
        n = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Por favor, introduce un número válido.")
        return

    # Avisar al usuario que estamos procesando (las APIs pueden tardar 2-3 segundos)
    await update.message.reply_chat_action("typing")

    # Obtener datos del bloque solicitado (N)
    data_n = get_block_data(n)
    if not data_n:
        await update.message.reply_text(f"⏳ El bloque {n} aún no existe o la API está saturada.")
        return

    # Obtener datos del bloque N+6
    n6 = n + 6
    data_n6 = get_block_data(n6)
    
    # Calcular próximo múltiplo de 144
    next_144, faltan = get_next_144_multiple(n)

    # --- CONSTRUCCIÓN DEL MENSAJE ---
    msg = f"🟦 **BLOQUE {n}**\n"
    msg += f"💰 Precio: `${data_n['price']:,.2f} USD`\n"
    msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n, 144) else '❌'}\n\n"

    if data_n6 and data_n['price']:
        # Comparativa Real
        symbol6 = "✔️" if data_n6['price'] > data_n['price'] else "❌"
        msg += f"🟩 **BLOQUE {n6} (N+6)**\n"
        msg += f"💰 Precio: `${data_n6['price']:,.2f} USD` {symbol6}\n"
        msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n6, 144) else '❌'}\n"
        
        diff = data_n6['price'] - data_n['price']
        msg += f"📈 Variación: `{'+' if diff > 0 else ''}{diff:,.2f} USD` \n\n"
    else:
        msg += f"🟩 **BLOQUE {n6}**\n⏳ Esperando confirmación o datos de precio...\n\n"

    # Sección de próximo objetivo
    msg += f"🎯 **Próximo Múltiplo 144:**\n"
    msg += f"➡️ Bloque: `{next_144}`\n"
    msg += f"⏳ Faltan: `{faltan}` bloques (aprox. {(faltan * 10) / 60:.1f} horas)"

    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    # Inicialización del Bot
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bloque", bloque))

    print("🚀 Bot iniciado correctamente...")
    application.run_polling()

if __name__ == "__main__":
    main()
