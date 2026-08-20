from django.core.management.base import BaseCommand

from core.models import Destination, Tour, TourGalleryImage

# Har bir shahar uchun WebSearch+WebFetch orqali joylashuvi tasdiqlangan (haqiqiy) rasm URL'lari.
# "Yo'nalishlar" bo'limi va "Tur" kartochkasi uchun alohida, bir-biriga mos rasmlar tanlangan.

DESTINATION_IMAGES = {
    "Antalya": "https://images.unsplash.com/photo-1641227059171-624465a39750?auto=format&fit=crop&w=500&q=75",
    "Male": "https://images.unsplash.com/photo-1573843981267-be1999ff37cd?auto=format&fit=crop&w=500&q=75",
    "Dubay": "https://images.unsplash.com/photo-1746731341047-76b2652ea843?auto=format&fit=crop&w=500&q=75",
    "Istanbul": "https://images.unsplash.com/photo-1759347171702-e9cae049bc01?auto=format&fit=crop&w=500&q=75",
    "Sharm El Sheikh": "https://images.unsplash.com/photo-1580058328338-5412e1123bf8?auto=format&fit=crop&w=500&q=75",
    "Batumi": "https://images.unsplash.com/photo-1593544482199-8395682901da?auto=format&fit=crop&w=500&q=75",
}

TOUR_IMAGES = {
    "Antalya": "https://images.unsplash.com/photo-1689130033348-1ebe2612a3d8?auto=format&fit=crop&w=800&q=75",
    "Maldiv": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&w=800&q=75",
    "Dubay": "https://images.unsplash.com/photo-1745750434535-5943ef2fd31a?auto=format&fit=crop&w=800&q=75",
    "Sharm El Sheikh": "https://images.unsplash.com/photo-1580058328338-5412e1123bf8?auto=format&fit=crop&w=800&q=75",
    "Istanbul": "https://images.unsplash.com/photo-1763965367191-6455ef032c79?auto=format&fit=crop&w=800&q=75",
    "Batumi": "https://images.unsplash.com/photo-1593544482199-8395682901da?auto=format&fit=crop&w=800&q=75",
}

TOUR_TO_DEST = {
    "Antalya": "Antalya",
    "Maldiv": "Male",
    "Dubay": "Dubay",
    "Sharm El Sheikh": "Sharm El Sheikh",
    "Istanbul": "Istanbul",
    "Batumi": "Batumi",
}


class Command(BaseCommand):
    help = (
        "Allaqachon bazada mavjud Yo'nalish, Tur va Tur-galereya rasmlarini "
        "to'g'ri (joylashuvi tekshirilgan) URL'larga yangilaydi. Bir necha marta "
        "ishga tushirish xavfsiz (idempotent)."
    )

    def handle(self, *args, **options):
        updated_dest = 0
        for dest in Destination.objects.all():
            url = DESTINATION_IMAGES.get(dest.name)
            if url and dest.image_url != url:
                dest.image_url = url
                dest.save(update_fields=["image_url"])
                updated_dest += 1

        updated_tour = 0
        for tour in Tour.objects.all():
            url = TOUR_IMAGES.get(tour.title)
            if url and tour.image_url != url:
                tour.image_url = url
                tour.save(update_fields=["image_url"])
                updated_tour += 1

        updated_gallery = 0
        dest_by_name = {d.name: d for d in Destination.objects.all()}
        for tour in Tour.objects.all():
            dest = dest_by_name.get(TOUR_TO_DEST.get(tour.title))
            if not dest or not dest.image_url:
                continue
            gallery_img = tour.gallery_images.filter(order=1).first()
            if gallery_img:
                if gallery_img.image_url != dest.image_url:
                    gallery_img.image_url = dest.image_url
                    gallery_img.save(update_fields=["image_url"])
                    updated_gallery += 1
            else:
                TourGalleryImage.objects.create(tour=tour, image_url=dest.image_url, order=1)
                updated_gallery += 1

        self.stdout.write(self.style.SUCCESS(
            f"Yangilandi: {updated_dest} ta yo'nalish, {updated_tour} ta tur, "
            f"{updated_gallery} ta galereya rasmi."
        ))
