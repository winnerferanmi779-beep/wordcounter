import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hello! Send me any text, and I will instantly analyze it for you.\n\n"
        "I'll count words, characters, sentences, paragraphs, and estimate the reading time!"
    )

# Text analysis handler
async def analyze_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    
    # 1. Character count (with and without spaces)
    char_count_with_spaces = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    
    # 2. Word count
    words = text.split()
    word_count = len(words)
    
    # 3. Sentence count (min 1 if text exists)
    sentences = [s for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    sentence_count = len(sentences) if word_count > 0 else 0
    
    # 4. Paragraph count
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # 5. Estimated Reading Time (Average: 200 words per minute)
    # WPM calculation: (word_count / 200) * 60 seconds
    reading_time_seconds = round((word_count / 200) * 60)
    
    if reading_time_seconds < 60:
        reading_time = f"{reading_time_seconds} seconds"
    else:
        minutes = reading_time_seconds // 60
        seconds = reading_time_seconds % 60
        reading_time = f"{minutes} min {seconds} sec" if seconds > 0 else f"{minutes} min"

    # Format the response message
    response = (
        f"📊 **Text Analysis:**\n\n"
        f"📝 **Words:** {word_count}\n"
        f"🔤 **Characters (w/ spaces):** {char_count_with_spaces}\n"
        f"🔤 **Characters (no spaces):** {char_count_no_spaces}\n"
        f"⏱ **Sentences:** {sentence_count}\n"
        f"Paragraphs:** {paragraph_count}\n"
        f"⏳ **Est. Reading Time:** {reading} if word_count > 0 else "0 seconds"
    )
    
    if word_count == 0:
        await update.message.reply_text("Please send some valid text to analyze!")
    else:
        await update.message.reply_text(response, parse_mode="Markdown")

def main() -> None:
    # Get token from environment variable (critical for Render deployment)
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    
    if not TOKEN:
        logger.error("No token found! Set the TELEGRAM_TOKEN environment variable.")
        return

    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_text))

    # Run the bot using long polling
    # Render's free tier works well with polling for background worker setups
    application.run_polling()

if __name__ == '__main__':
    main()
