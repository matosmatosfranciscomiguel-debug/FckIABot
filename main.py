import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Servidor web dummy para mantener vivo el Web Service en Render
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot activo")

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# Lógica del Bot
client = genai.Client(api_key=GEMINI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    system_instruction = (
        "Eres un asistente personal y académico eficiente. Ayudas al usuario con sus tareas de la universidad, "
        "organización de entregas, resúmenes, código y redacción de mensajes."
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Ocurrió un error: {str(e)}")

if __name__ == "__main__":
    # Iniciar servidor HTTP en segundo plano
    threading.Thread(target=run_web_server, daemon=True).start()

    # Iniciar bot de Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot activo en Telegram...")
    app.run_polling()
