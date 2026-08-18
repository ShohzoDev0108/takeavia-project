import datetime

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import translate_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.utils.translation import override

from .models import Destination, Lead, Testimonial, Tour


def switch_language(request):
    """Til almashtirish uchun maxsus view.

    Django'ning standart `set_language` view'i shu loyihada ishlamaydi:
    biz `i18n_patterns(..., prefix_default_language=False)` ishlatamiz
    (standart til — o'zbekcha — manzilda prefikssiz, masalan `/boglanish/`),
    lekin standart `/i18n/setlang/` manzilining o'zi HAM prefikssiz bo'lgani
    uchun, Django uni har doim "standart til" so'rovi deb hisoblaydi va
    foydalanuvchi aslida ruscha/inglizcha sahifada turgan bo'lsa ham buni
    e'tiborga olmaydi — natijada "ruschadan o'zbekchaga qaytish" ishlamay
    qoladi (manzil tarjima qilinmay, o'sha tilda qolib ketadi).

    Shu sababli joriy tilni shablon o'zi (`{{ LANGUAGE_CODE }}`) orqali
    aniq yuborib beradi, va biz shu tilni asos qilib manzilni qo'lda
    tarjima qilamiz.
    """
    next_url = request.POST.get("next") or "/"
    if not url_has_allowed_host_and_scheme(
        url=next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = "/"

    valid_codes = {code for code, _name in settings.LANGUAGES}
    lang_code = request.POST.get("language")
    current_lang = request.POST.get("current")
    if current_lang not in valid_codes:
        current_lang = settings.LANGUAGE_CODE

    if request.method == "POST" and lang_code in valid_codes:
        with override(current_lang):
            next_url = translate_url(next_url, lang_code)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        return response
    return HttpResponseRedirect(next_url)


def home(request):
    """Bosh sahifa — barcha bo'limlar ma'lumotlar bazasidan olinadi."""
    # Qidiruv formasidagi "Ketish/Qaytish sanasi" har doim BUGUNGI kunga
    # nisbatan avtomatik hisoblanadi (avval qattiq yozilgan "20.05.2026" kabi
    # sana o'tib ketgach eskirib, mijozlarga chalkash ko'rinardi).
    today = datetime.date.today()
    default_depart = today + datetime.timedelta(days=7)
    default_return = default_depart + datetime.timedelta(days=7)
    context = {
        "destinations": Destination.objects.all(),
        "tours": Tour.objects.filter(is_active=True)[:6],
        "testimonials": Testimonial.objects.filter(is_active=True)[:3],
        "default_depart_date": default_depart.strftime("%d.%m.%Y"),
        "default_return_date": default_return.strftime("%d.%m.%Y"),
    }
    return render(request, "core/index.html", context)


def tour_list(request):
    """Barcha faol turlar sahifasi. ?q= bilan filtrlash mumkin."""
    q = request.GET.get("q", "").strip()
    tours = Tour.objects.filter(is_active=True)
    if q:
        tours = tours.filter(title__icontains=q)
    return render(request, "core/tour_list.html", {"tours": tours, "q": q})


def tour_detail(request, pk):
    """Tur haqida batafsil + bron qilish formasi."""
    tour = get_object_or_404(Tour, pk=pk, is_active=True)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        contact = request.POST.get("contact", "").strip()
        if contact:
            Lead.objects.create(kind="booking", tour=tour, name=name, contact=contact)
            messages.success(
                request,
                _("\"%(title)s\" turi uchun so'rovingiz qabul qilindi! Menejerlarimiz tez orada bog'lanadi.")
                % {"title": tour.title},
            )
            return redirect("core:tour_detail", pk=tour.pk)
        messages.error(request, _("Iltimos, telefon raqamingiz yoki emailingizni kiriting."))

    similar = Tour.objects.filter(is_active=True).exclude(pk=tour.pk)[:3]
    return render(request, "core/tour_detail.html", {"tour": tour, "similar": similar})


def flight_search(request):
    """Aviabilet qidiruv formasi — so'rovni bazaga yozib, mos turlarni ko'rsatadi."""
    if request.method != "POST":
        return redirect("core:home")

    from_city = request.POST.get("from_city", "").strip()
    to_city = request.POST.get("to_city", "").strip()
    depart_date = request.POST.get("depart_date", "").strip()
    return_date = request.POST.get("return_date", "").strip()
    passengers = request.POST.get("passengers", "").strip()

    Lead.objects.create(
        kind="flight",
        from_city=from_city,
        to_city=to_city,
        depart_date=depart_date,
        return_date=return_date,
        passengers=passengers,
    )

    matching_tours = Tour.objects.filter(is_active=True)
    if to_city:
        matching_tours = matching_tours.filter(title__icontains=to_city)

    context = {
        "from_city": from_city or _("Toshkent (TAS)"),
        "to_city": to_city,
        "depart_date": depart_date,
        "return_date": return_date,
        "passengers": passengers or _("2 kishi, Economy"),
        "tours": matching_tours,
    }
    return render(request, "core/search_results.html", context)


def leave_request(request):
    """CTA forma — email/telefon qoldirish."""
    if request.method == "POST":
        contact = request.POST.get("contact", "").strip()
        if contact:
            Lead.objects.create(kind="contact", contact=contact)
            messages.success(
                request,
                _("So'rovingiz qabul qilindi! Menejerlarimiz tez orada siz bilan bog'lanadi."),
            )
        else:
            messages.error(request, _("Iltimos, email yoki telefon raqamingizni kiriting."))
    return redirect("core:home")


def about(request):
    """'Biz haqimizda' sahifasi — kompaniya haqida, statistika va afzalliklar."""
    return render(request, "core/about.html")


def contact(request):
    """'Bog'lanish' sahifasi — aloqa ma'lumotlari va xabar qoldirish formasi."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        contact_value = request.POST.get("contact", "").strip()
        message = request.POST.get("message", "").strip()
        if contact_value and message:
            Lead.objects.create(kind="message", name=name, contact=contact_value, message=message)
            messages.success(
                request,
                _("Xabaringiz qabul qilindi! Menejerlarimiz tez orada siz bilan bog'lanadi."),
            )
            return redirect("core:contact")
        messages.error(request, _("Iltimos, aloqa ma'lumotingiz va xabar matningizni kiriting."))
    return render(request, "core/contact.html")
