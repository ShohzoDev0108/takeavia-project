"""SEO bilan bog'liq yordamchi ko'rinishlar: sitemap.xml va robots.txt.

django.contrib.sites ilovasiga bog'liq bo'lmaslik uchun (domenni qo'lda
sozlash o'rniga) so'rovning o'zidan (request.build_absolute_uri) to'liq
manzil olinadi — bu domen productionda o'zgarsa ham ishlayveradi.
"""
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import override

from .models import Tour

LANGUAGE_CODES = [code for code, _ in settings.LANGUAGES]

# (url_name, changefreq, priority) — saytning statik sahifalari
STATIC_PAGES = [
    ("core:home", "weekly", "1.0"),
    ("core:tour_list", "daily", "0.9"),
    ("core:contact", "monthly", "0.6"),
    ("core:about", "monthly", "0.5"),
]


def _alternates(request, url_name, kwargs=None):
    """Har bir til uchun to'liq (absolute) manzillar lug'ati: {"uz": "...", "ru": "...", ...}."""
    kwargs = kwargs or {}
    result = {}
    for lang in LANGUAGE_CODES:
        with override(lang):
            path = reverse(url_name, kwargs=kwargs)
        result[lang] = request.build_absolute_uri(path)
    return result


def _url_entry(alternates, changefreq, priority, lastmod=None):
    """Bitta <url> blokini (barcha til variantlari hreflang bilan) hosil qiladi."""
    links = "".join(
        f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}"/>\n'
        for lang, href in alternates.items()
    )
    default_href = alternates.get(settings.LANGUAGE_CODE)
    if default_href:
        links += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{default_href}"/>\n'

    lastmod_xml = ""
    if lastmod:
        lastmod_xml = f"    <lastmod>{lastmod.date().isoformat()}</lastmod>\n"

    entries = []
    for loc in alternates.values():
        entries.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"{lastmod_xml}"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"{links}"
            "  </url>\n"
        )
    return "".join(entries)


def sitemap_view(request):
    """Ko'p tilli sitemap.xml — har bir sahifaning uz/ru/en variantlari va
    ular orasidagi hreflang bog'lanishlari bilan (Google Search Console uchun)."""
    body = []

    for url_name, changefreq, priority in STATIC_PAGES:
        alternates = _alternates(request, url_name)
        body.append(_url_entry(alternates, changefreq, priority))

    for tour in Tour.objects.filter(is_active=True).order_by("order", "id"):
        alternates = _alternates(request, "core:tour_detail", {"pk": tour.pk})
        lastmod = getattr(tour, "updated_at", None)
        body.append(_url_entry(alternates, "weekly", "0.8", lastmod))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "".join(body)
        + "</urlset>\n"
    )
    return HttpResponse(xml, content_type="application/xml")


def robots_view(request):
    """robots.txt — qidiruv botlariga ruxsat etilgan/etilmagan bo'limlar va sitemap manzili."""
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /sorov/",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
