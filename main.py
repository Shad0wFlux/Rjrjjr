import logging
import ssl
import smtplib
import shutil
from pathlib import Path
from uuid import uuid4
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import os

# الخطوات
EMAIL, PASSWORD, SUBJECT, BODY, PDF, EMAILS = range(6)

# إعداد اللوج
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SMTP
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

# مسار الملفات المؤقتة
BASE_TMP = Path("/tmp/jobmailer_bot")
BASE_TMP.mkdir(exist_ok=True)

# ---- Helpers ----
def get_user_dir(user_id: int) -> Path:
    path = BASE_TMP / str(user_id)
    path.mkdir(exist_ok=True)
    return path

def cleanup_user_dir(user_id: int):
    path = BASE_TMP / str(user_id)
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)

# ---- Conversation ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً 👋 أرسل لي إيميل Gmail الخاص بك:")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text.strip()
    await update.message.reply_text("تمام ✅ الآن أرسل الباسورد (App Password):")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["password"] = update.message.text.strip()
    await update.message.reply_text("أرسل موضوع الرسالة (Subject):")
    return SUBJECT

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text.strip()
    await update.message.reply_text("أرسل نص الرسالة (Body):")
    return BODY

async def get_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["body"] = update.message.text.strip()
    await update.message.reply_text("الآن أرسل ملف PDF:")
    return PDF

async def get_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("من فضلك أرسل ملف PDF.")
        return PDF

    user_dir = get_user_dir(update.message.from_user.id)
    file = await update.message.document.get_file()
    unique_name = f"{uuid4()}_{update.message.document.file_name}"
    pdf_path = user_dir / unique_name
    await file.download_to_drive(pdf_path)
    context.user_data["pdf"] = pdf_path

    await update.message.reply_text("أرسل لستة الإيميلات (ملف txt أو نص كل إيميل في سطر):")
    return EMAILS

async def get_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_dir = get_user_dir(update.message.from_user.id)
    emails = []

    if update.message.document:
        file = await update.message.document.get_file()
        from uuid import uuid4
        txt_path = user_dir / f"{uuid4()}_emails.txt"
        await file.download_to_drive(txt_path)
        lines = txt_path.read_text(encoding="utf-8").splitlines()
        emails = [e.strip() for e in lines if "@" in e]
    else:
        lines = update.message.text.splitlines()
        emails = [e.strip() for e in lines if "@" in e]

    valid_emails = []
    for e in emails:
        try:
            v = validate_email(e).email
            valid_emails.append(v)
        except EmailNotValidError:
            continue

    if not valid_emails:
        await update.message.reply_text("❌ لم أجد إيميلات صحيحة. أرسل من جديد:")
        return EMAILS

    context.user_data["emails"] = valid_emails

    progress_msg = await update.message.reply_text(
        f"📤 جاري الإرسال إلى {len(valid_emails)} إيميل...\n"
    )

    results = []
    for idx, to_addr in enumerate(valid_emails, 1):
        ok, err = await send_email(
            context.user_data["email"],
            context.user_data["password"],
            to_addr,
            context.user_data["subject"],
            context.user_data["body"],
            context.user_data["pdf"],
        )
        if ok:
            results.append(f"[{idx}/{len(valid_emails)}] ✅ {to_addr}")
        else:
            results.append(f"[{idx}/{len(valid_emails)}] ❌ {to_addr} — {err}")

        await progress_msg.edit_text("📊 تقدم الإرسال:\n" + "\n".join(results))

    context.user_data.clear()
    cleanup_user_dir(update.message.from_user.id)
    return ConversationHandler.END

# ---- Send email ----
async def send_email(email_addr, password, to_addr, subject, body, attachment: Path):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_addr
    msg["To"] = to_addr
    msg.set_content(body)

    if attachment:
        data = attachment.read_bytes()
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=attachment.name)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=60) as server:
            server.login(email_addr, password)
            server.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)

# ---- Main ----
def main():
    TOKEN = os.getenv("8107977783:AAGZC9-ZZR1PKfi0fTdy6mT2NdnSYVVyb0Y")
    if not TOKEN:
        raise ValueError("❌ مافي توكن، ضيف TOKEN في Render Environment Variables")

    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT, get_email)],
            PASSWORD: [MessageHandler(filters.TEXT, get_password)],
            SUBJECT: [MessageHandler(filters.TEXT, get_subject)],
            BODY: [MessageHandler(filters.TEXT, get_body)],
            PDF: [MessageHandler(filters.Document.PDF, get_pdf)],
            EMAILS: [MessageHandler(filters.TEXT | filters.Document.TEXT, get_emails)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
