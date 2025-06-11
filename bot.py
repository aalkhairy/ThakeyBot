### config.py
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = "tasks.db"


### database.py
import sqlite3
from config import DB_NAME

def init_db():
    """Initialize the database and create tasks table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    user_id INTEGER,
                    task TEXT
                )''')
    conn.commit()
    conn.close()

def add_task(user_id, task):
    """Insert a new task for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user_id, task))
    conn.commit()
    conn.close()

def get_tasks(user_id):
    """Retrieve all tasks associated with a specific user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT rowid, task FROM tasks WHERE user_id = ?", (user_id,))
    results = c.fetchall()
    conn.close()
    return results

def delete_task(user_id, task_id):
    """Delete a task based on its ID and user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE rowid = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()


### bot.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import init_db, add_task, get_tasks, delete_task

# Initialize the database
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command and show the main menu."""
    keyboard = [
        ["➕ إضافة مهمة", "📋 عرض المهام"],
        ["✅ إنهاء مهمة"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "👋 مرحبًا بك في *ذكي بوت*!\n"
        "اختر أحد الأوامر من الأزرار بالأسفل 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all current tasks for the user."""
    tasks = get_tasks(update.effective_user.id)
    if tasks:
        reply = "📝 مهامك الحالية:\n"
        for rowid, task in tasks:
            reply += f"{rowid}. {task}\n"
    else:
        reply = "📭 لا توجد مهام حالياً."
    await update.message.reply_text(reply)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button inputs and user interactions."""
    text = update.message.text.strip()

    if text == "➕ إضافة مهمة":
        await update.message.reply_text("✏️ أرسل لي المهمة التي تريد إضافتها:")
        context.user_data['adding'] = True

    elif text == "📋 عرض المهام":
        await list_tasks(update, context)

    elif text == "✅ إنهاء مهمة":
        await update.message.reply_text("🆔 أرسل رقم المهمة التي تريد حذفها:")
        context.user_data['deleting'] = True

    elif context.user_data.get('adding'):
        add_task(update.effective_user.id, text)
        await update.message.reply_text(f"✅ تمت إضافة المهمة: {text}")
        context.user_data['adding'] = False

    elif context.user_data.get('deleting'):
        if text.isdigit():
            delete_task(update.effective_user.id, int(text))
            await update.message.reply_text(f"🗑️ تم حذف المهمة رقم {text}")
        else:
            await update.message.reply_text("❗️يرجى إرسال رقم صحيح.")
        context.user_data['deleting'] = False

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    app.run_polling()


### requirements.txt
python-telegram-bot==20.3


### Procfile
worker: python bot.py


### .gitignore
__pycache__/
*.pyc
tasks.db
