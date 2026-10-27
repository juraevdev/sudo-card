# UzNext E-Card

JizPi IT Park talaba kirish kartasi: Flutter ilova + FastAPI access backend.

QR kodda **shaxsiy ma’lumot yo‘q** — faqat opaque token (`UZN.<token>`). Kirish ruxsatini turniket/skaner `POST /access/verify` orqali backend’dan oladi.

## Tezkor start

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Seed login: `SA-104237` / `park2026`  
API docs: http://127.0.0.1:8000/docs

### 2. Flutter

```bash
flutter pub get
flutter run
```

Android emulator uchun:

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Haqiqiy telefon uchun `API_BASE_URL` ni kompyuteringiz LAN IP’siga qo‘ying.

## Arxitektura

1. Talaba login → JWT  
2. `GET /card/me` → karta + `qrPayload`  
3. Skanner QR o‘qiydi → `POST /access/verify` + `X-Scanner-Key`  
4. Backend: revoked / expired / unknown tekshiradi → `allowed`

Batafsil: [backend/README.md](backend/README.md)
