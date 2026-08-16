# Take Avia Trip

Aviabiletlar va tur paketlar uchun sayohat agentligi sayti. Django 5 asosida qurilgan.

## Imkoniyatlar

- Bosh sahifa: qidiruv formasi, mashhur yo'nalishlar, hot turlar, mijozlar fikri — hammasi ma'lumotlar bazasidan boshqariladi
- Tur paketlar ro'yxati (`/turlar/`) va har bir tur uchun batafsil sahifa + bron qilish formasi (`/tur/<id>/`)
- Aviabilet qidiruv so'rovlari va barcha murojaatlar bazaga yoziladi
- Admin panel (`/admin/`) — turlar, yo'nalishlar, mijoz fikrlari va murojaatlarni boshqarish (o'zbek tilida)
- To'liq responsiv dizayn (mobil / planshet / desktop)

## O'rnatish (lokal)

```bash
git clone <repo-url>
cd takeavia_project
python -m venv venv
venv\Scripts\activate        # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed         # boshlang'ich ma'lumotlar (turlar, yo'nalishlar...)
python manage.py createsuperuser
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/ — Admin: http://127.0.0.1:8000/admin/

## Serverga chiqarish (production)

To'liq, bosqichma-bosqich (Hetzner + Ubuntu + Nginx + Gunicorn + Let's Encrypt)
qo'llanma uchun **[`deploy/DEPLOY.md`](deploy/DEPLOY.md)** ga qarang. U yerda
tayyor Nginx (`deploy/nginx_takeavia.conf`) va systemd (`deploy/takeavia-gunicorn.service`)
konfiguratsiya fayllari ham bor.

Qisqacha: `.env.example` faylini ko'ring. Serverda quyidagi muhit o'zgaruvchilari SHART:

| O'zgaruvchi | Qiymat |
|---|---|
| `DJANGO_SECRET_KEY` | yangi maxfiy kalit (pastda) |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_ALLOWED_HOSTS` | `sizning-domen.uz,www.sizning-domen.uz` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://sizning-domen.uz` |

Yangi maxfiy kalit yaratish:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`DEBUG=false` bo'lganda xavfsizlik sozlamalari (HTTPS redirect, secure cookie, HSTS) avtomatik yoqiladi, dev-kalit bilan ishga tushirish esa taqiqlanadi.

Statik fayllarni yig'ish:

```bash
python manage.py collectstatic
```

## Tuzilma

```
takeavia_project/
├── manage.py
├── requirements.txt
├── deploy/            # serverga joylashtirish uchun qo'llanma va konfiguratsiya
│   ├── DEPLOY.md
│   ├── nginx_takeavia.conf
│   └── takeavia-gunicorn.service
├── takeavia/          # loyiha sozlamalari (settings, urls, wsgi)
└── core/              # asosiy ilova
    ├── models.py      # Destination, Tour, Testimonial, Lead
    ├── views.py       # sahifalar va formalar logikasi
    ├── admin.py       # admin panel sozlamalari
    ├── management/commands/seed.py   # boshlang'ich ma'lumotlar
    └── templates/core/               # sahifa shablonlari
```

Eslatma: `db.sqlite3` git'ga qo'shilmaydi — har bir muhitda `migrate` + `seed` bilan yangi baza yaratiladi.
