# Take Avia Trip — serverga joylashtirish qo'llanmasi

Bu qo'llanma Hetzner'da yaratilgan `takeavia` serveriga (Ubuntu, IP: `95.217.128.222`)
loyihani birinchi marta joylashtirish uchun. Har bir buyruqni ketma-ket bajaring.

Domen nomi bo'lgan joylarda **`takeavia.uz`** yozilgan — buni har doim
o'zingizning haqiqiy domeningizga almashtiring (nginx faylida, `.env`da va h.k.).

---

## 0. Serverga ulanish

Windows'da PowerShell yoki PuTTY orqali:

```bash
ssh root@95.217.128.222
```

---

## 1. Tizimni yangilash va kerakli dasturlarni o'rnatish

```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip nginx git ufw
```

---

## 2. Xavfsizlik devori (firewall)

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

`y` deb tasdiqlang (SSH orqali ulanishni yo'qotmaslik uchun `OpenSSH`ni albatta oldin qo'shing).

---

## 3. Loyiha kodini serverga joylashtirish

Repo (`github.com/ShohzoDev0108/takeavia-project`) **private** bo'lgani uchun
oddiy `git clone` ishlamaydi — server GitHub oldida "tanilishi" kerak. Buning
uchun eng to'g'ri yo'l — **Deploy Key** (serverga xos, faqat o'qish huquqiga
ega SSH kalit; muddati tugamaydi, "keyingi safar yangilash" bo'limidagi
`git pull` ham shu kalit orqali ishlayveradi).

**3.1. Serverda maxsus SSH kalit yaratish** (parolsiz — avtomatik `git pull`
uchun kerak):

```bash
ssh-keygen -t ed25519 -C "takeavia-server-deploy" -f ~/.ssh/takeavia_deploy_key -N ""
cat ~/.ssh/takeavia_deploy_key.pub
```

Oxirgi buyruq ekranga bitta qator matn chiqaradi (`ssh-ed25519 AAAA...` bilan
boshlanadi) — shu qatorni to'liq nusxalab oling.

**3.2. Bu kalitni GitHub'ga "Deploy key" sifatida qo'shish:**

1. Brauzerda: `https://github.com/ShohzoDev0108/takeavia-project/settings/keys`
2. **Add deploy key** tugmasini bosing
3. Title: masalan `Hetzner server`
4. Key maydoniga nusxalangan matnni joylang
5. **"Allow write access"ni BELGILAMANG** (faqat o'qish huquqi yetarli va xavfsizroq)
6. **Add key** bosing

**3.3. Serverga shu kalitdan foydalanishni buyurish:**

```bash
cat >> ~/.ssh/config << 'EOF'
Host github.com
    IdentityFile ~/.ssh/takeavia_deploy_key
    User git
EOF
chmod 600 ~/.ssh/config
ssh -T git@github.com
```

Oxirgi buyruq `Hi ShohzoDev0108/takeavia-project! You've successfully
authenticated...` deb javob berishi kerak (birinchi marta "authenticity...
continue connecting?" deb so'rasa — `yes` yozing).

**3.4. Kodni klonlash:**

```bash
mkdir -p /var/www
cd /var/www
git clone git@github.com:ShohzoDev0108/takeavia-project.git takeavia_project
```

---

*Muqobil yo'l (agar keyinchalik repo public qilinsa yoki git ishlatilmasa)* —
kompyuteringizdan to'g'ridan-to'g'ri serverga yuklash: Windows'da **WinSCP**
yoki **FileZilla** dasturi orqali (SFTP protokoli, host: `95.217.128.222`,
user: `root`) butun loyiha papkasini `/var/www/takeavia_project` ichiga
nusxalang. `db.sqlite3`, `venv/`, `__pycache__/`, `staticfiles/`, `media/`
papka/fayllarini yuklash shart emas — ular serverda qaytadan yaratiladi.

---

## 4. Virtual muhit va kutubxonalarni o'rnatish

```bash
cd /var/www/takeavia_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 5. `.env` faylini yaratish

```bash
cp .env.example .env
nano .env
```

Yangi maxfiy kalit yaratish uchun (alohida terminalda yoki shu yerda):

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`.env` faylini quyidagicha to'ldiring (o'z domeningiz bilan):

```
DJANGO_SECRET_KEY=<yuqorida generatsiya qilingan kalit>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=takeavia.uz,www.takeavia.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://takeavia.uz,https://www.takeavia.uz
```

Saqlab chiqing (`nano`da: `Ctrl+O`, `Enter`, `Ctrl+X`).

---

## 6. Bazani tayyorlash

```bash
cd /var/www/takeavia_project
source venv/bin/activate
set -a; source .env; set +a
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

`createsuperuser` — admin panelga kirish uchun login/parol so'raydi, o'zingiz kiritasiz.

---

## 7. Gunicorn'ni doimiy xizmat sifatida sozlash

```bash
cp /var/www/takeavia_project/deploy/takeavia-gunicorn.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now takeavia-gunicorn
systemctl status takeavia-gunicorn
```

`active (running)` deb yashil rangda chiqishi kerak. Agar xato bo'lsa, sababini
ko'rish uchun:

```bash
journalctl -u takeavia-gunicorn -e
```

---

## 8. Nginx sozlash

```bash
cp /var/www/takeavia_project/deploy/nginx_takeavia.conf /etc/nginx/sites-available/takeavia.uz
nano /etc/nginx/sites-available/takeavia.uz   # domen nomini tekshiring/almashtiring
ln -s /etc/nginx/sites-available/takeavia.uz /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

Shu bosqichdan so'ng sayt `http://95.217.128.222` yoki (agar DNS allaqachon
ishlagan bo'lsa) `http://takeavia.uz` manzilida ochilishi kerak (hali https'siz).

---

## 9. Domenni serverga yo'naltirish (DNS)

Domen sotib olingan joyning boshqaruv paneliga kiring va DNS yozuvlar (DNS records)
bo'limiga quyidagilarni qo'shing:

| Tur | Nomi | Qiymat |
|---|---|---|
| A | `@` | `95.217.128.222` |
| A | `www` | `95.217.128.222` |

DNS o'zgarishi butun dunyoga tarqalishi (propagation) bir necha daqiqadan bir
necha soatgacha vaqt olishi mumkin. `nslookup takeavia.uz` buyrug'i bilan
tekshirib borishingiz mumkin.

---

## 10. SSL sertifikat (HTTPS) — bepul, Let's Encrypt orqali

DNS ishlay boshlagach (domen serverning IP-manziliga ko'rsatgach):

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d takeavia.uz -d www.takeavia.uz
```

Savol beriladi — email kiritasiz, shartlarga roziligingizni bildirasiz, va
"http'dan https'ga avtomatik yo'naltirilsinmi" so'ralganda **ha** deb javob bering.
Certbot avtomatik ravishda Nginx faylini yangilaydi va sertifikatni 90 kunda bir
avtomatik yangilab turadi (qo'shimcha sozlash shart emas).

---

## 11. Yakuniy tekshirish

- `https://takeavia.uz` — bosh sahifa ochilishi, rasm/animatsiya ko'rinishi
- `https://takeavia.uz/admin/` — admin panelga kirish
- Qidiruv formasi orqali so'rov yuborib ko'rish, admin panelda ko'rinishini tekshirish
- `https://takeavia.uz/sitemap.xml` va `/robots.txt` ochilishini tekshirish
- Uch tilni ham tekshirish (UZ/RU/EN — yuqoridagi til almashtirgich orqali)

---

## Keyingi safar kodni yangilashda (deploy)

Kelgusida saytga o'zgarish kiritilganda, serverda shu qadamlarni bajarasiz:

```bash
cd /var/www/takeavia_project
git pull                              # yoki fayllarni qo'lda yangilash
source venv/bin/activate
pip install -r requirements.txt       # yangi kutubxona qo'shilgan bo'lsa
set -a; source .env; set +a
python manage.py migrate              # yangi migratsiya bo'lsa
python manage.py collectstatic --noinput
sudo systemctl restart takeavia-gunicorn
```

---

## Muammo yuzaga kelsa

| Muammo | Qayerni tekshirish |
|---|---|
| Sayt ochilmayapti (502 Bad Gateway) | `systemctl status takeavia-gunicorn`, `journalctl -u takeavia-gunicorn -e` |
| Statik fayllar (CSS/rasm) yo'q | `collectstatic` bajarilganmi? Nginx `/static/` yo'li to'g'rimi? |
| "DisallowedHost" xatosi | `.env`dagi `DJANGO_ALLOWED_HOSTS` domeningizni o'z ichiga oladimi? |
| SSL ishlamayapti | DNS to'liq tarqalganmi (`nslookup`)? `certbot --nginx` qayta ishga tushiring |
| Formadan yuborilgan ma'lumot saqlanmayapti | `DJANGO_CSRF_TRUSTED_ORIGINS`da `https://` bilan to'g'ri domen bormi? |
