import telebot
import ssl
import smtplib
import shutil
import time
from pathlib import Path
from uuid import uuid4
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError

# التوكن
TOKEN = "8107977783:AAFoXs7pVssS02C5CTNd_K0XBoEc047SGtI"
bot = telebot.TeleBot(TOKEN)

# إعدادات SMTP
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

# ملفات مؤقتة
BASE_TMP = Path("/tmp/jobmailer_bot")
BASE_TMP.mkdir(exist_ok=True)

# ذاكرة مؤقتة لكل مستخدم
user_data = {}
user_state = {}  # الحالة الحالية لكل مستخدم


def get_user_dir(user_id: int) -> Path:
    path = BASE_TMP / str(user_id)
    path.mkdir(exist_ok=True)
    return path


def cleanup_user_dir(user_id: int):
    path = BASE_TMP / str(user_id)
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


# ---- البداية ----
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    # نبدأ من جديد ونمسح أي بيانات قديمة
    user_data[user_id] = {}
    user_state[user_id] = "EMAIL"
    cleanup_user_dir(user_id)

    bot.reply_to(message, "أهلاً 👋 أرسل لي إيميل Gmail الخاص بك:")


@bot.message_handler(func=lambda m: True, content_types=['text', 'document'])
def handle_message(message):
    user_id = message.chat.id
    state = user_state.get(user_id)

    if not state:
        bot.reply_to(message, "اكتب /start عشان تبدأ 👋")
        return

    # --- EMAIL ---
    if state == "EMAIL":
        user_data[user_id]["email"] = message.text.strip()
        user_state[user_id] = "PASSWORD"
        bot.reply_to(message, "تمام ✅ الآن أرسل الباسورد (App Password):")

    # --- PASSWORD ---
    elif state == "PASSWORD":
        user_data[user_id]["password"] = message.text.strip()
        user_state[user_id] = "SUBJECT"
        bot.reply_to(message, "أرسل موضوع الرسالة (Subject):")

    # --- SUBJECT ---
    elif state == "SUBJECT":
        user_data[user_id]["subject"] = message.text.strip()
        user_state[user_id] = "BODY"
        bot.reply_to(message, "أرسل نص الرسالة (Body):")

    # --- BODY ---
    elif state == "BODY":
        user_data[user_id]["body"] = message.text.strip()
        user_state[user_id] = "PDF"
        bot.reply_to(message, "الآن أرسل ملف PDF:")

    # --- PDF ---
    elif state == "PDF":
        if not message.document or not message.document.mime_type == "application/pdf":
            bot.reply_to(message, "❌ لازم ترسل ملف PDF.")
            return

        user_dir = get_user_dir(user_id)
        file_info = bot.get_file(message.document.file_id)
        unique_name = f"{uuid4()}_{message.document.file_name}"
        pdf_path = user_dir / unique_name
        downloaded = bot.download_file(file_info.file_path)
        pdf_path.write_bytes(downloaded)

        user_data[user_id]["pdf"] = pdf_path
        user_state[user_id] = "EMAILS"
        bot.reply_to(message, "أرسل لستة الإيميلات (ملف txt أو نص كل إيميل في سطر):")

    # --- EMAILS ---
    elif state == "EMAILS":
        emails = []
        user_dir = get_user_dir(user_id)

        if message.document:  # ملف txt
            file_info = bot.get_file(message.document.file_id)
            txt_path = user_dir / f"{uuid4()}_emails.txt"
            downloaded = bot.download_file(file_info.file_id)
            txt_path.write_bytes(downloaded)
            lines = txt_path.read_text(encoding="utf-8").splitlines()
            emails = [e.strip() for e in lines if "@" in e]
        else:  # نص
            lines = message.text.splitlines()
            emails = [e.strip() for e in lines if "@" in e]

        valid_emails = []
        for e in emails:
            try:
                v = validate_email(e).email
                valid_emails.append(v)
            except EmailNotValidError:
                continue

        if not valid_emails:
            bot.reply_to(message, "❌ لم أجد إيميلات صحيحة. أرسل من جديد:")
            return

        bot.reply_to(message, f"📤 جاري الإرسال إلى {len(valid_emails)} إيميل...")

        results = []
        for idx, to_addr in enumerate(valid_emails, 1):
            ok, err = send_email(
                user_data[user_id]["email"],
                user_data[user_id]["password"],
                to_addr,
                user_data[user_id]["subject"],
                user_data[user_id]["body"],
                user_data[user_id]["pdf"],
            )
            if ok:
                results.append(f"[{idx}/{len(valid_emails)}] ✅ {to_addr}")
            else:
                results.append(f"[{idx}/{len(valid_emails)}] ❌ {to_addr} — {err}")

            bot.send_message(user_id, "\n".join(results))

        bot.send_message(user_id, "✅ تم الإرسال بالكامل. نتمنى لك التوفيق 🌹")

        cleanup_user_dir(user_id)
        user_data.pop(user_id, None)
        user_state.pop(user_id, None)


# ---- إرسال الإيميل ----
def send_email(email_addr, password, to_addr, subject, body, attachment: Path):
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


# ---- Run (with auto-restart) ----
def run_bot():
    while True:
        try:
            print("🚀 Bot is running...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"❌ خطأ: {e} — إعادة تشغيل خلال 5 ثواني")
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
