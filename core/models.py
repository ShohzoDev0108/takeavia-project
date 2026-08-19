from django.db import models


class Destination(models.Model):
    """Toshkentdan mashhur reyslar — bosh sahifadagi aviachipta kartalari."""

    name = models.CharField("Shahar nomi", max_length=100, help_text="Masalan: Istanbul")
    country = models.CharField("Mamlakat", max_length=100)
    flag_code = models.CharField(
        "Bayroq kodi", max_length=2,
        help_text="ISO kod: tr, ae, eg, ge, mv va h.k."
    )
    from_code = models.CharField("Qayerdan (IATA)", max_length=4, default="TAS")
    to_code = models.CharField(
        "Qayerga (IATA)", max_length=4, default="",
        help_text="Aeroport kodi, masalan: IST, DXB, AYT"
    )
    image = models.ImageField(
        "Rasm", upload_to="destinations/", blank=True, null=True,
        help_text="Kompyuteringizdan rasm tanlang.",
    )
    image_url = models.URLField(
        "Rasm URL (zaxira)", max_length=500, blank=True,
        help_text="Faqat yuqorida rasm yuklanmagan holatda ishlatiladi.",
    )
    price_from = models.PositiveIntegerField(
        "Taxminiy narx ($)", help_text="Bir tomonlama/borish-qaytish taxminiy narx, $"
    )
    duration = models.CharField(
        "Parvoz vaqti", max_length=50,
        help_text="Masalan: 3 soat 40 daqiqa"
    )
    is_popular = models.BooleanField("Mashhur belgisi", default=False)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Mashhur reys"
        verbose_name_plural = "Mashhur reyslar"

    def __str__(self):
        return f"{self.from_code} → {self.to_code} ({self.name})"

    @property
    def image_src(self):
        """Shablonlarda ishlatish uchun: yuklangan fayl bo'lsa o'shani, bo'lmasa URL'ni qaytaradi."""
        if self.image:
            return self.image.url
        return self.image_url


class Tour(models.Model):
    """Hot Tours — issiq tur paketlari."""

    UZ_MONTHS = [
        "", "yanvar", "fevral", "mart", "aprel", "may", "iyun",
        "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr",
    ]

    title = models.CharField("Nomi", max_length=150)
    description = models.TextField(
        "Tavsif (o'zbekcha)", blank=True, default="",
        help_text="Tur haqida batafsil matn — SEO uchun muhim. Har bir xatboshi yangi qatordan.",
    )
    description_ru = models.TextField(
        "Tavsif (ruscha)", blank=True, default="",
        help_text="Bo'sh qoldirilsa, rus sahifada o'zbekcha tavsif ko'rsatiladi.",
    )
    description_en = models.TextField(
        "Tavsif (inglizcha)", blank=True, default="",
        help_text="Bo'sh qoldirilsa, ingliz sahifada o'zbekcha tavsif ko'rsatiladi.",
    )
    image = models.ImageField(
        "Rasm", upload_to="tours/", blank=True, null=True,
        help_text="Kompyuteringizdan rasm tanlang.",
    )
    image_url = models.URLField(
        "Rasm URL (zaxira)", max_length=500, blank=True,
        help_text="Faqat yuqorida rasm yuklanmagan holatda ishlatiladi.",
    )
    duration = models.CharField("Muddat", max_length=50, help_text="Masalan: 7 kecha / 8 kun")
    hotel_label = models.CharField("Mehmonxona", max_length=50, default="5* Hotel")
    includes = models.CharField("Nimalar kiradi", max_length=200, default="Aviabilet + Mehmonxona + Transfer")
    price = models.PositiveIntegerField("Narx ($)")
    depart_date = models.DateField("Ketish sanasi", null=True, blank=True)
    return_date = models.DateField("Qaytish sanasi", null=True, blank=True)
    seats_left = models.PositiveIntegerField("Qolgan joylar", default=5)
    rating = models.DecimalField("Reyting", max_digits=2, decimal_places=1, default=5.0)
    is_active = models.BooleanField("Faol", default=True)
    order = models.PositiveIntegerField("Tartib", default=0)
    updated_at = models.DateTimeField("Yangilangan vaqti", auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Tur"
        verbose_name_plural = "Turlar"

    def __str__(self):
        return f"{self.title} — ${self.price}"

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    @property
    def description_display(self):
        """Joriy sayt tiliga mos tavsifni qaytaradi (bo'sh bo'lsa — o'zbekchaga qaytadi)."""
        from django.utils.translation import get_language

        lang = (get_language() or "uz").split("-")[0]
        if lang == "ru" and self.description_ru:
            return self.description_ru
        if lang == "en" and self.description_en:
            return self.description_en
        return self.description

    @property
    def dates_display(self):
        """Ketish/qaytish sanalaridan '20 – 27 may' ko'rinishidagi matnni avtomatik hosil qiladi."""
        d, r = self.depart_date, self.return_date
        if not d:
            return ""
        if not r:
            return f"{d.day} {self.UZ_MONTHS[d.month]}"
        if d.month == r.month:
            return f"{d.day} – {r.day} {self.UZ_MONTHS[d.month]}"
        return f"{d.day} {self.UZ_MONTHS[d.month]} – {r.day} {self.UZ_MONTHS[r.month]}"


class TourGalleryImage(models.Model):
    """Tur 'batafsil' sahifasida asosiy rasmdan tashqari ko'rsatiladigan qo'shimcha rasmlar.

    Asosiy rasm (Tour.image) katta bo'lib yuqorida turadi, bu yerdagi rasmlar esa
    uning ostida kichikroq bo'lib, bosilganda asosiy o'rniga almashadi (jami 4 tagacha rasm).
    """

    tour = models.ForeignKey(
        Tour, verbose_name="Tur", on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ImageField(
        "Rasm", upload_to="tours/gallery/", blank=True, null=True,
        help_text="Kompyuteringizdan rasm tanlang.",
    )
    image_url = models.URLField(
        "Rasm URL (zaxira)", max_length=500, blank=True,
        help_text="Faqat yuqorida rasm yuklanmagan holatda ishlatiladi.",
    )
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Tur galereyasi rasmi"
        verbose_name_plural = "Tur galereyasi rasmlari (asosiysidan tashqari, 3 tagacha)"

    def __str__(self):
        return f"{self.tour.title} — qo'shimcha rasm #{self.order}"

    @property
    def image_src(self):
        """Shablonlarda ishlatish uchun: yuklangan fayl bo'lsa o'shani, bo'lmasa URL'ni qaytaradi."""
        if self.image:
            return self.image.url
        return self.image_url


class Testimonial(models.Model):
    """Mijozlarimiz fikri."""

    name = models.CharField("Ism-familiya", max_length=100)
    city = models.CharField("Shahar", max_length=100)
    avatar_url = models.URLField("Avatar URL", max_length=500, blank=True)
    text = models.TextField("Fikr matni (o'zbekcha)")
    text_ru = models.TextField(
        "Fikr matni (ruscha)", blank=True, default="",
        help_text="Bo'sh qoldirilsa, rus sahifada o'zbekcha matn ko'rsatiladi.",
    )
    text_en = models.TextField(
        "Fikr matni (inglizcha)", blank=True, default="",
        help_text="Bo'sh qoldirilsa, ingliz sahifada o'zbekcha matn ko'rsatiladi.",
    )
    rating = models.PositiveSmallIntegerField("Baho (1-5)", default=5)
    is_active = models.BooleanField("Ko'rsatilsin", default=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Mijoz fikri"
        verbose_name_plural = "Mijozlar fikri"

    def __str__(self):
        return f"{self.name} ({self.city})"

    @property
    def text_display(self):
        from django.utils.translation import get_language

        lang = (get_language() or "uz").split("-")[0]
        if lang == "ru" and self.text_ru:
            return self.text_ru
        if lang == "en" and self.text_en:
            return self.text_en
        return self.text


class Lead(models.Model):
    """So'rov qoldirish formasi va aviabilet qidiruvlaridan kelgan murojaatlar."""

    KIND_CHOICES = [
        ("contact", "So'rov (CTA forma)"),
        ("flight", "Aviabilet qidiruvi"),
        ("booking", "Tur bron qilish"),
        ("message", "Bog'lanish sahifasidagi xabar"),
    ]

    kind = models.CharField("Turi", max_length=10, choices=KIND_CHOICES, default="contact")
    name = models.CharField("Ism", max_length=150, blank=True)
    contact = models.CharField("Aloqa (email/telefon)", max_length=200, blank=True)
    message = models.TextField("Xabar matni", blank=True)
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
        return f"{self.name or self.contact} ({self.created_at:%d.%m.%Y})"


class SiteSettings(models.Model):
    """Sayt bo'ylab ishlatiladigan aloqa ma'lumotlari — bitta yozuv, admin panelda tahrirlanadi."""

    phone_1 = models.CharField("Telefon 1", max_length=30, default="+998 77 210 54 00")
    phone_2 = models.CharField("Telefon 2 (ixtiyoriy)", max_length=30, blank=True, default="+998 77 210 83 71")
    email_1 = models.EmailField("Email 1", max_length=254, default="takeavia1@gmail.com")
    email_2 = models.EmailField("Email 2 (ixtiyoriy)", max_length=254, blank=True, default="info@takeavia.uz")
    address = models.CharField("Manzil", max_length=255, default="Mirzo Ulug'bek, Parkent ko'chasi, 51")
    working_hours = models.CharField("Ish vaqti", max_length=100, default="Har kuni, 24/7")
    latitude = models.DecimalField(
        "Xarita — kenglik (latitude)", max_digits=9, decimal_places=6, default=41.318567,
        help_text="Pastdagi xaritada belgini bosib yoki sudrab aniq joyni tanlang.",
    )
    longitude = models.DecimalField(
        "Xarita — uzunlik (longitude)", max_digits=9, decimal_places=6, default=69.315329,
    )
    telegram_url = models.URLField(
        "Telegram havolasi", max_length=300, blank=True, default="",
        help_text="Masalan: https://t.me/sizning_kanal — bo'sh qoldirilsa, ikonka sahifada ko'rsatilmaydi.",
    )
    instagram_url = models.URLField(
        "Instagram havolasi", max_length=300, blank=True, default="",
        help_text="Masalan: https://instagram.com/sizning_sahifa",
    )
    facebook_url = models.URLField(
        "Facebook havolasi", max_length=300, blank=True, default="",
    )
    youtube_url = models.URLField(
        "YouTube havolasi", max_length=300, blank=True, default="",
    )

    class Meta:
        verbose_name = "Sayt sozlamalari"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return "Sayt sozlamalari (aloqa ma'lumotlari)"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
