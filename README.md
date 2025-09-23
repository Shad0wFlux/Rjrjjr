# JobMailer Bot

بوت تليجرام لإرسال رسائل جماعية مع ملف PDF كمرفق.

## التشغيل على Render

1. ارفع هذا المشروع على GitHub.
2. أنشئ خدمة جديدة على [Render](https://render.com/).
3. اختر **Web Service** أو **Worker**.
4. اربط المستودع.
5. في Environment Variables أضف:
   - `TOKEN` = التوكن من BotFather
6. Render بيشغل الأمر:
   ```bash
   python main.py
   ```

## التشغيل محلياً

```bash
pip install -r requirements.txt
python main.py
```
