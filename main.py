import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURACIÓN ---
TOKEN = "8725996090:AAF44XD_l4TpymdFrEareVG-RpYH_OM8kzg"
API_PRICE = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
MEMPOOL_API = "https://mempool.space/api"

# Variable global para simular el precio del bloque anterior en la prueba
ultimo_precio_registrado = 64000.0 

def get_price():
    try:
        r = requests.get(API_PRICE).json()
        return float(r["bitcoin"]["usd"])
    except:
        return None

def check_block(height):
    try:
        r = requests.get(f"{MEMPOOL_API}/block-height/{height}")
        return r.text if r.status_code == 200 else None
    except:
        return None

def is_multiple(n, base):
    return n % base == 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot de prueba Bitcoin activo.\nUsa /bloque <numero>")

async def bloque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ultimo_precio_registrado
    
    if not context.args:
        await update.message.reply_text("❌ Indica el número de bloque: /bloque 840000")
        return

    try:
        n = int(context.args[0])
    except:
        await update.message.reply_text("❌ Número no válido.")
        return

    # Verificar si el bloque existe
    block_hash = check_block(n)
    if not block_hash:
        await update.message.reply_text(f"⏳ El bloque {n} aún no ha sido minado.")
        return

    # Obtener precio actual y comparar
    price_now = get_price()
    if price_now is None:
        await update.message.reply_text("⚠️ Error al obtener el precio.")
        return

    # Lógica del símbolo (Compara precio actual vs el último que guardó el bot)
    symbol = "✔️" if price_now >= ultimo_precio_registrado else "❌"
    
    msg = f"🟦 **BLOQUE {n}**\n"
    msg += f"💰 Precio BTC: `${price_now:,.2f} USD` {symbol}\n"
    msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n, 144) else '❌'}\n"
    msg += f"⚙️ Múltiplo 2016: {'✔️' if is_multiple(n, 2016) else '❌'}\n\n"

    # Bloque N+6
    n6 = n + 6
    if check_block(n6):
        msg += f"🟩 **BLOQUE {n6} (N+6)**\n"
        msg += f"✅ Confirmado\n"
        msg += f"📊 Múltiplo 144: {'✔️' if is_multiple(n6, 144) else '❌'}\n"
    else:
        msg += f"🟩 **BLOQUE {n6} (N+6)**\n"
        msg += f"⏳ Esperando minado..."

    # Actualizamos el "precio anterior" para la siguiente consulta de prueba
    ultimo_precio_registrado = price_now

    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    # Usando la versión asíncrona de la librería (v20+)
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bloque", bloque))

    print("🤖 Bot iniciado con el token proporcionado...")
    app.run_polling()

if __name__ == "__main__":
    main()
