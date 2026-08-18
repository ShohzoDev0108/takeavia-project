"""
Tashqi (Unsplash va h.k.) rasm URL'larini serverning o'ziga ko'chiradi.

Nima uchun: tashqi CDN'dan rasm yuklash sekin, Google Core Web Vitals'ni
yomonlashtiradi va tashqi xizmatga bog'liqlik yaratadi. Bu buyruq har bir
Destination/Tour'ning image_url'ini yuklab, WebP formatida siqib, lokal
ImageField'ga saqlaydi (shablonlar avtomatik lokal faylni ishlata boshlaydi,
chunki image_src avval image'ni, keyin image_url'ni tekshiradi).

Shuningdek bosh sahifa hero foni va "Biz haqimizda" rasmi ham
MEDIA_ROOT/site/ ichiga yuklab olinadi.

Ishlatish (serverda, venv faollashtirilgan holda):
    python manage.py localize_images

Xavfsiz va idempotent: allaqachon lokal rasmi bor obyektlarni o'tkazib yuboradi.
"""

import io
import os
import urllib.request

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from core.models import Destination, Tour

# Sahifa shablonlarida ishlatiladigan statik sahifa rasmlari
SITE_IMAGES = {
    # nom: (URL, maks. kenglik)
    "hero.webp": ("https://images.unsplash.com/photo-1470214203634-e436a8848e23?auto=format&fit=crop&w=1600&q=80", 1600),
    "about.webp": ("https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=800&q=75", 800),
}


def _download(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (takeavia-image-localizer)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _to_webp(raw_bytes, max_width):
    """Rasmni ochib, kerak bo'lsa kichraytirib, WebP (sifat 80) qilib qaytaradi."""
    from PIL import Image

    img = Image.open(io.BytesIO(raw_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if img.width > max_width:
        new_h = round(img.height * max_width / img.width)
        img = img.resize((max_width, new_h), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="WEBP", quality=80, method=6)
    return out.getvalue()


class Command(BaseCommand):
    help = "Tashqi rasm URL'larini lokalga (WebP, siqilgan) ko'chiradi."

    def handle(self, *args, **options):
        ok, failed = 0, 0

        # 1) Sahifa rasmlari (hero, about)
        site_dir = os.path.join(settings.MEDIA_ROOT, "site")
        os.makedirs(site_dir, exist_ok=True)
        for fname, (url, width) in SITE_IMAGES.items():
            path = os.path.join(site_dir, fname)
            if os.path.exists(path):
                self.stdout.write(f"Bor, o'tkazildi: site/{fname}")
                continue
            try:
                data = _to_webp(_download(url), width)
                with open(path, "wb") as f:
                    f.write(data)
                ok += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Yuklandi: site/{fname} ({len(data) // 1024} KB)"))
            except Exception as e:  # noqa: BLE001
                failed += 1
                self.stderr.write(f"XATO site/{fname}: {e}")

        # 2) Destination kartalari (200x250 karta uchun 2x = 400px yetarli)
        for d in Destination.objects.all():
            if d.image or not d.image_url.startswith("http"):
                continue
            try:
                data = _to_webp(_download(d.image_url), 500)
                d.image.save(f"{d.to_code or d.pk}.webp".lower(), ContentFile(data), save=True)
                ok += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Yuklandi: {d.name} ({len(data) // 1024} KB)"))
            except Exception as e:  # noqa: BLE001
                failed += 1
                self.stderr.write(f"XATO {d.name}: {e}")

        # 3) Tur kartalari (420px balandlik uchun 2x = 900px kenglik yetarli)
        for t in Tour.objects.all():
            if t.image or not t.image_url.startswith("http"):
                continue
            try:
                data = _to_webp(_download(t.image_url), 900)
                slug = t.title.lower().replace(" ", "-")
                t.image.save(f"{slug}.webp", ContentFile(data), save=True)
                ok += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Yuklandi: {t.title} ({len(data) // 1024} KB)"))
            except Exception as e:  # noqa: BLE001
                failed += 1
                self.stderr.write(f"XATO {t.title}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Tayyor: {ok} ta yuklandi, {failed} ta xato."))
        if failed:
            self.stderr.write(
                "Xato bo'lganlarni keyinroq qayta ishga tushiring — "
                "buyruq faqat yetishmayotganlarni yuklaydi.")
