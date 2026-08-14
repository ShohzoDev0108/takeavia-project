from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Destination, Lead, Testimonial, Tour


def home(request):
    """Bosh sahifa — barcha bo'limlar ma'lumotlar bazasidan olinadi."""
    context = {
        "destinations": Destination.objects.all(),
        "tours": Tour.objects.filter(is_active=True)[:6],
        "testimonials": Testimonial.objects.filter(is_active=True)[:3],
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
                f"\"{tour.title}\" turi uchun so'rovingiz qabul qilindi! "
                "Menejerlarimiz tez orada bog'lanadi.",
            )
            return redirect("core:tour_detail", pk=tour.pk)
        messages.error(request, "Iltimos, telefon raqamingiz yoki emailingizni kiriting.")

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
        "from_city": from_city or "Toshkent (TAS)",
        "to_city": to_city,
        "depart_date": depart_date,
        "return_date": return_date,
        "passengers": passengers or "2 kishi, Economy",
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
                "So'rovingiz qabul qilindi! Menejerlarimiz tez orada siz bilan bog'lanadi.",
            )
        else:
            messages.error(request, "Iltimos, email yoki telefon raqamingizni kiriting.")
    return redirect("core:home")
