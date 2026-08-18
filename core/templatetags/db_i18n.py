"""
Ma'lumotlar bazasidan keladigan (admin panelda o'zbekcha kiritiladigan) matnlarni
RU/EN sahifalarda avtomatik tarjima qiluvchi shablon filtri.

Muammo: {% trans %} faqat shablondagi qotirilgan matnlarni tarjima qiladi,
bazadagi qiymatlar ("Turkiya", "4 soat", "7 kecha / 8 kun", "20 – 27 may"...)
esa har uch tilda ham o'zbekcha ko'rinib qolardi.

Yechim: |dbtr filtri — joriy til RU yoki EN bo'lsa, avval butun matnni
lug'atdan qidiradi, topilmasa so'zma-so'z (token) almashtiradi.
O'zbek tilida esa matnni o'zgartirmasdan qaytaradi.

Admin panelga yangi yo'nalish/tur qo'shilsa, quyidagi lug'atlarga mos
so'zlarni qo'shib borish kifoya (davlat nomlari, shaharlar va h.k.).
"""

import re

from django import template
from django.utils.translation import get_language

register = template.Library()

# ---- To'liq mos kelish lug'ati (butun matn shu ko'rinishda bo'lsa) ----
EXACT = {
    "ru": {
        # Davlatlar / hududlar
        "Turkiya": "Турция",
        "BAA": "ОАЭ",
        "Misr": "Египет",
        "Gruziya": "Грузия",
        "Mahar orollari": "Мальдивы",
        "Maldiv orollari": "Мальдивы",
        "O'zbekiston": "Узбекистан",
        # Shaharlar (mijoz fikrlari)
        "Toshkent": "Ташкент",
        "Samarqand": "Самарканд",
        "Buxoro": "Бухара",
        # Tur tarkibi
        "Aviabilet + Mehmonxona + Transfer": "Авиабилет + Отель + Трансфер",
        # Tur muddatlari (rus tilida son-so'z mosligi uchun aniq yozilgan)
        "7 kecha / 8 kun": "7 ночей / 8 дней",
        "4 kecha / 5 kun": "4 ночи / 5 дней",
        "3 kecha / 4 kun": "3 ночи / 4 дня",
        "Har kuni, 24/7": "Ежедневно, 24/7",
    },
    "en": {
        "Turkiya": "Turkey",
        "BAA": "UAE",
        "Misr": "Egypt",
        "Gruziya": "Georgia",
        "Mahar orollari": "Maldives",
        "Maldiv orollari": "Maldives",
        "O'zbekiston": "Uzbekistan",
        "Toshkent": "Tashkent",
        "Samarqand": "Samarkand",
        "Buxoro": "Bukhara",
        "Aviabilet + Mehmonxona + Transfer": "Flight + Hotel + Transfer",
        "7 kecha / 8 kun": "7 nights / 8 days",
        "4 kecha / 5 kun": "4 nights / 5 days",
        "3 kecha / 4 kun": "3 nights / 4 days",
        "Har kuni, 24/7": "Every day, 24/7",
    },
}

# ---- So'zma-so'z almashtirish (uzun iboralar birinchi turishi SHART) ----
TOKENS = {
    "ru": [
        ("ko'chish bilan", "с пересадкой"),
        ("Mahar orollari", "Мальдивы"),
        ("Maldiv orollari", "Мальдивы"),
        ("Aviabilet", "Авиабилет"),
        ("Mehmonxona", "Отель"),
        ("Transfer", "Трансфер"),
        ("Turkiya", "Турция"),
        ("Gruziya", "Грузия"),
        ("Misr", "Египет"),
        ("BAA", "ОАЭ"),
        ("daqiqa", "мин."),
        ("soat", "ч."),
        ("kecha", "ноч."),
        ("kun", "дн."),
        # Oy nomlari (sana oralig'ida qaratqich kelishigi: "20 – 27 мая")
        ("yanvar", "января"), ("fevral", "февраля"), ("mart", "марта"),
        ("aprel", "апреля"), ("may", "мая"), ("iyun", "июня"),
        ("iyul", "июля"), ("avgust", "августа"), ("sentabr", "сентября"),
        ("oktabr", "октября"), ("noyabr", "ноября"), ("dekabr", "декабря"),
    ],
    "en": [
        ("ko'chish bilan", "with layover"),
        ("Mahar orollari", "Maldives"),
        ("Maldiv orollari", "Maldives"),
        ("Aviabilet", "Flight"),
        ("Mehmonxona", "Hotel"),
        ("Transfer", "Transfer"),
        ("Turkiya", "Turkey"),
        ("Gruziya", "Georgia"),
        ("Misr", "Egypt"),
        ("BAA", "UAE"),
        ("daqiqa", "min"),
        ("soat", "h"),
        ("kecha", "nights"),
        ("kun", "days"),
        ("yanvar", "January"), ("fevral", "February"), ("mart", "March"),
        ("aprel", "April"), ("may", "May"), ("iyun", "June"),
        ("iyul", "July"), ("avgust", "August"), ("sentabr", "September"),
        ("oktabr", "October"), ("noyabr", "November"), ("dekabr", "December"),
    ],
}


def _normalize(text):
    """Turli apostrof belgilarini (' va ') bir xil ASCII ' ga keltiradi."""
    return text.replace("‘", "'").replace("’", "'").replace("ʼ", "'")


@register.filter(name="dbtr")
def dbtr(value):
    """Bazadagi o'zbekcha matnni joriy sayt tiliga (ru/en) moslab beradi."""
    if value is None:
        return ""
    text = str(value)
    lang = (get_language() or "uz").split("-")[0]
    if lang not in ("ru", "en"):
        return text  # o'zbek tili — asl holicha

    normalized = _normalize(text).strip()

    # 1) Butun matn lug'atda bo'lsa — darhol qaytaramiz
    exact = EXACT[lang].get(normalized)
    if exact:
        return exact

    # 2) Bo'lmasa — so'zma-so'z almashtiramiz (so'z chegaralari bilan,
    #    "may" faqat alohida so'z sifatida almashadi)
    result = normalized
    for src, dst in TOKENS[lang]:
        pattern = r"(?<![\w'])" + re.escape(src) + r"(?![\w'])"
        result = re.sub(pattern, dst, result)
    return result
