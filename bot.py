from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN
from database import init_db, add_task, get_tasks, delete_task

# تهيئة قاعدة البيانات عند بدء البوت
init_db()

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في ذكي بوت!\n"
        "أنا مساعدك اليومي الذكي لإدارة المهام.\n\n"
        "الأوامر المتاحة:\n"
        "/add <مهمتك> ➕ لإضافة مهمة\n"
        "/list 📋 لعرض المهام\n"
        "/done <رقم> ✅ لحذف مهمة"
    )

# أمر /add لإضافة مهمة
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = " ".join(context.args)
    if task:
        add_task(update.effective_user.id, task)
        await update.message.reply_text(f"✅ تم إضافة المهمة: {task}")
    else:
        await update.message.reply_text("❗️يرجى كتابة المهمة بعد الأمر /add")

# أمر /list لعرض المهام
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = get_tasks(update.effective_user.id)
    if tasks:
        reply = "📝 مهامك الحالية:\n"
        for rowid, task in tasks:
            reply += f"{rowid}. {task}\n"
    else:
        reply = "📭 لا توجد مهام حالياً."
    await update.message.reply_text(reply)

# أمر /done لحذف مهمة
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].isdigit():
        task_id = int(context.args[0])
        delete_task(update.effective_user.id, task_id)
        await update.message.reply_text(f"✅ تم حذف المهمة رقم {task_id}")
    else:
        await update.message.reply_text("❗️يرجى كتابة رقم المهمة بعد /done")

# تشغيل البوت
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("done", done))
    app.run_polling()
