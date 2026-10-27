# UzNext E-Card Access API

IT Park kirish nazorati uchun FastAPI backend.

QR kod ichida **PII yo‘q** — faqat opaque token (`UZN.<token>`). Turniket/skaner har safar `/access/verify` chaqiradi.

## Ishga tushirish

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # yoki: cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs: http://127.0.0.1:8000/docs

## Seed foydalanuvchi

| Maydon | Qiymat |
|--------|--------|
| Student ID | `SA-104237` |
| Password | `park2026` |
| Card ID | `UZN-2026-0142` |

## API

### Talaba ilovasi

- `POST /auth/login` — `{ "studentId", "password" }` → JWT
- `GET /card/me` — `Authorization: Bearer <jwt>` → karta + `qrPayload`

### Skanner / turniket

- `POST /access/verify`
  - Header: `X-Scanner-Key: <SCANNER_API_KEY>`
  - Body: `{ "token": "<QR raw string>", "gate": "main-entrance" }`
  - Javob: `{ "allowed": true/false, "reason": "ok|expired|revoked|..." }`

## Muhim

- Production’da `SECRET_KEY` va `SCANNER_API_KEY` ni almashtiring.
- SQLite faqat boshlash uchun; campus uchun PostgreSQL tavsiya etiladi.
- Karta bekor qilish (`revoked`) keyinroq admin endpoint orqali qo‘shiladi.
