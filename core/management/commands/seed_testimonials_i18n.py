"""
Mijoz fikrlariga (Testimonial) rus/ingliz tarjimalarini yozadi.

Nima uchun alohida buyruq: `seed.py` faqat jadval BO'SH bo'lsa
Testimonial yozuvlarini yaratadi — productiondagi sayt allaqachon shu 3 ta
fikrni saqlagan, shuning uchun ularga tarjima maydonlarini (text_ru,
text_en) to'ldirish uchun mavjud yozuvlarni ism+shahar bo'yicha topib,
alohida yangilaymiz (idempotent, --force bo'lmasa mavjud tarjimani bosib
o'tmaydi).

Ishlatish:
    python manage.py seed_testimonials_i18n
    python manage.py seed_testimonials_i18n --force   # tarjimalarni qayta yozadi
"""

from django.core.management.base import BaseCommand

from core.models import Testimonial

TRANSLATIONS = {
    ("Dilshoda Karimova", "Toshkent"): {
        "ru": (
            "Мы ездили отдыхать в Анталью, обслуживание было просто отличным. "
            "Всё было организовано чётко и вовремя. Спасибо, Take Avia Trip!"
        ),
        "en": (
            "We went on vacation to Antalya, and the service was excellent. "
            "Everything was organized clearly and on time. Thank you, Take Avia Trip!"
        ),
    },
    ("Jahongir Norqulov", "Samarqand"): {
        "ru": (
            "Наша поездка в Дубай была незабываемой. Особенно порадовали "
            "трансфер и обслуживание в отеле."
        ),
        "en": (
            "Our trip to Dubai was unforgettable. We were especially happy "
            "with the transfer and hotel service."
        ),
    },
    ("Sitora Alimova", "Buxoro"): {
        "ru": (
            "Мальдивы были местом моей мечты. Мы съездили по лучшей цене "
            "благодаря Take Avia Trip! Рекомендую."
        ),
        "en": (
            "The Maldives were my dream destination. We got there at the "
            "best price thanks to Take Avia Trip! Highly recommend."
        ),
    },
}


class Command(BaseCommand):
    help = "Mijoz fikrlariga rus/ingliz tarjimalarini yozadi (ism+shahar bo'yicha moslashtirib)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Mavjud tarjimalarni ham qayta yozadi.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        updated = 0
        for t in Testimonial.objects.all():
            key = (t.name, t.city)
            tr = TRANSLATIONS.get(key)
            if not tr:
                continue
            if not force and (t.text_ru or t.text_en):
                continue
            t.text_ru = tr["ru"]
            t.text_en = tr["en"]
            t.save(update_fields=["text_ru", "text_en"])
            updated += 1
            self.stdout.write(self.style.SUCCESS(f"Tarjima yozildi: {t.name}"))

        self.stdout.write(self.style.SUCCESS(f"Jami yangilandi: {updated} ta fikr."))
