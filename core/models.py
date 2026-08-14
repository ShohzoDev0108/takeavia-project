from django.db import models


class Destination(models.Model):
    """Mashhur yo'nalishlar — bosh sahifadagi kartalar."""

    name = models.CharField("Nomi", max_length=100)
    country = models.CharField("Mamlakat", max_length=100)
    flag_code = models.CharField(
        "Bayroq kodi", max_length=2,
        help_text="ISO kod: tr, ae, eg, ge, mv va h.k."
    )
    image_url = models.URLField("Rasm URL", max_length=500)
    price_from = models.PositiveIntegerField("Narx ($, ...dan)")
    duration = models.CharField("Muddat", max_length=50, help_text="Masalan: 7 kecha / 8 kun")
    is_popular = models.BooleanField("Mashhur belgisi", default=False)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"

    def __str__(self):
        return f"{self.name} ({self.country})"


class Tour(models.Model):
    """Hot Tours — issiq tur paketlari."""

    title = models.CharField("Nomi", max_length=150)
    image_url = models.URLField("Rasm URL", max_length=500)
    duration = models.CharField("Muddat", max_length=50, help_text="Masalan: 7 kecha / 8 kun")
    hotel_label = models.CharField("Mehmonxona", max_length=50, default="5* Hotel")
    includes = models.CharField("Nimalar kiradi", max_length=200, default="Aviabilet + Mehmonxona + Transfer")
    price = models.PositiveIntegerField("Narx ($)")
    dates = models.CharField("Sanalar", max_length=60, help_text="Masalan: 20 – 27 May")
    seats_left = models.PositiveIntegerField("Qolgan joylar", default=5)
    rating = models.DecimalField("Reyting", max_digits=2, decimal_places=1, default=5.0)
    is_active = models.BooleanField("Faol", default=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Tur"
        verbose_name_plural = "Turlar"

    def __str__(self):
        return f"{self.title} — ${self.price}"


class Testimonial(models.Model):
    """Mijozlarimiz fikri."""

    name = models.CharField("Ism-familiya", max_length=100)
    city = models.CharField("Shahar", max_length=100)
    avatar_url = models.URLField("Avatar URL", max_length=500, blank=True)
    text = models.TextField("Fikr matni")
    rating = models.PositiveSmallIntegerField("Baho (1-5)", default=5)
    is_active = models.BooleanField("Ko'rsatilsin", default=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Mijoz fikri"
        verbose_name_plural = "Mijozlar fikri"

    def __str__(self):
        return f"{self.name} ({self.city})"


class Lead(models.Model):
    """So'rov qoldirish formasi va aviabilet qidiruvlaridan kelgan murojaatlar."""

    KIND_CHOICES = [
        ("contact", "So'rov (CTA forma)"),
        ("flight", "Aviabilet qidiruvi"),
        ("booking", "Tur bron qilish"),
    ]

    kind = models.CharField("Turi", max_length=10, choices=KIND_CHOICES, default="contact")
    name = models.CharField("Ism", max_length=150, blank=True)
    contact = models.CharField("Aloqa (email/telefon)", max_length=200, blank=True)
    tour = models.ForeignKey(
        "Tour", verbose_name="Tur", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="bookings",
    )
    from_city = models.CharField("Qayerdan", max_length=100, blank=True)
    to_city = models.CharField("Qayerga", max_length=100, blank=True)
    depart_date = models.CharField("Ketish sanasi", max_length=30, blank=True)
    return_date = models.CharField("Qaytish sanasi", max_length=30, blank=True)
    passengers = models.CharField("Yo'lovchilar", max_length=60, blank=True)
    created_at = models.DateTimeField("Yaratilgan vaqt", auto_now_add=True)
    is_processed = models.BooleanField("Ko'rib chiqildi", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"

    def __str__(self):
        if self.kind == "flight":
            return f"{self.from_city} → {self.to_city} ({self.created_at:%d.%m.%Y})"
        if self.kind == "booking" and self.tour:
            return f"{self.name or self.contact} — {self.tour.title} ({self.created_at:%d.%m.%Y})"
        return f"{self.contact} ({self.created_at:%d.%m.%Y})"
