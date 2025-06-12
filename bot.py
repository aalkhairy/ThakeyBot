
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# إعداد السجل
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# الحالات
ADD_TODO, ADD_REMINDER = range(2)

# تخزين مؤقت
user_data_store = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 مهامي", callback_data='todo')],
        [InlineKeyboardButton("⏰ تذكير", callback_data='reminder')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
    "👋 أهلاً بك  أنا ذكي بوت \nاختر ما ترغب في فعله:",
    reply_markup=reply_markup
)

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'todo':
        await query.edit_message_text("📝 أرسل المهمة التي ترغب في إضافتها:")
        return ADD_TODO
    elif query.data == 'reminder':
        await query.edit_message_text("⏰ أرسل الوقت الذي تريد أن أذكرك فيه (مثال: 10 دقائق):")
        return ADD_REMINDER

# إضافة مهمة
async def add_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task = update.message.text
    user_data_store.setdefault(user_id, {}).setdefault("todos", []).append(task)
    await update.message.reply_text(f"✅ تمت إضافة المهمة: {task}")
    return ConversationHandler.END

# إضافة تذكير
async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    time_text = update.message.text.lower()

    minutes = 0
    if 'دقيقة' in time_text:
        minutes = int(''.join(filter(str.isdigit, time_text)))
    elif 'min' in time_text or 'm' in time_text:
        minutes = int(''.join(filter(str.isdigit, time_text)))
    else:
        await update.message.reply_text("❗️لم أفهم الوقت، الرجاء الإرسال مثل: 10 دقائق")
        return ConversationHandler.END

    await update.message.reply_text(f"⏳ سيتم تذكيرك خلال {minutes} دقيقة...")
    await asyncio.sleep(minutes * 60)
    await context.bot.send_message(chat_id=user_id, text="🔔 هذا تذكيرك!")

    return ConversationHandler.END

# إلغاء
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم الإلغاء.")
    return ConversationHandler.END

# تشغيل البوت
def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            ADD_TODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_todo)],
            ADD_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_reminder)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
