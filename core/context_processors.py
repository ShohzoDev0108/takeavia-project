from django.conf import settings
from django.urls import translate_url

from .models import SiteSettings

# Open Graph uchun til kodlari (Facebook/Telegram "uz_UZ" ko'rinishini kutadi,
# oddiy "uz" emas).
_OG_LOCALE_MAP = {"uz": "uz_UZ", "ru": "ru_RU", "en": "en_US"}


def site_settings(request):
    """Har bir shablonga 'site_settings' o'zgaruvchisini qo'shadi (telefon, email, manzil va h.k.)."""
    return {"site_settings": SiteSettings.load()}


def seo(request):
    """Har bir sahifaga SEO uchun kerakli o'zgaruvchilarni qo'shadi:
    canonical havola, uch tildagi hreflang alternativlari va Open Graph
    lokali. `core/_seo.html` shu o'zgaruvchilardan foydalanadi."""
    path = request.path
    canonical = request.build_absolute_uri(path)

    alternates = {}
    for lang, _name in settings.LANGUAGES:
        try:
            translated_path = translate_url(path, lang)
        except Exception:
            translated_path = path
        alternates[lang] = request.build_absolute_uri(translated_path)

    default_lang = settings.LANGUAGE_CODE
    current_lang = getattr(request, "LANGUAGE_CODE", default_lang)

    ss = SiteSettings.load()
    social_links = [
        url for url in (ss.telegram_url, ss.instagram_url, ss.facebook_url, ss.youtube_url) if url
    ]

    return {
        "seo_canonical_url": canonical,
        "seo_hreflang_alternates": alternates,
        "seo_x_default_url": alternates.get(default_lang, canonical),
        "seo_og_locale": _OG_LOCALE_MAP.get(current_lang, "uz_UZ"),
        "seo_og_locale_alternates": [
            code for lang, code in _OG_LOCALE_MAP.items() if lang != current_lang
        ],
        "seo_social_links": social_links,
    }
