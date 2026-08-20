import datetime

from django.core.management.base import BaseCommand

from core.models import Destination, Testimonial, Tour, TourGalleryImage


class Command(BaseCommand):
    help = "Saytni boshlang'ich ma'lumotlar bilan to'ldiradi (mavjudlarini o'chirmaydi)."

    def handle(self, *args, **options):
        if not Destination.objects.exists():
            Destination.objects.bulk_create([
                Destination(name="Antalya", country="Turkiya", flag_code="tr",
                            to_code="AYT",
                            image_url="https://images.unsplash.com/photo-1641227059171-624465a39750?auto=format&fit=crop&w=500&q=75",
                            price_from=180, duration="4 soat", is_popular=True, order=1),
                Destination(name="Male", country="Maldiv orollari", flag_code="mv",
                            to_code="MLE",
                            image_url="https://images.unsplash.com/photo-1573843981267-be1999ff37cd?auto=format&fit=crop&w=500&q=75",
                            price_from=450, duration="9 soat (ko'chish bilan)", order=2),
                Destination(name="Dubay", country="BAA", flag_code="ae",
                            to_code="DXB",
                            image_url="https://images.unsplash.com/photo-1746731341047-76b2652ea843?auto=format&fit=crop&w=500&q=75",
                            price_from=150, duration="2 soat 40 daqiqa", is_popular=True, order=3),
                Destination(name="Istanbul", country="Turkiya", flag_code="tr",
                            to_code="IST",
                            image_url="https://images.unsplash.com/photo-1759347171702-e9cae049bc01?auto=format&fit=crop&w=500&q=75",
                            price_from=190, duration="5 soat", is_popular=True, order=4),
                Destination(name="Sharm El Sheikh", country="Misr", flag_code="eg",
                            to_code="SSH",
                            image_url="https://images.unsplash.com/photo-1580058328338-5412e1123bf8?auto=format&fit=crop&w=500&q=75",
                            price_from=260, duration="5 soat 30 daqiqa", order=5),
                Destination(name="Batumi", country="Gruziya", flag_code="ge",
                            to_code="BUS",
                            image_url="https://images.unsplash.com/photo-1593544482199-8395682901da?auto=format&fit=crop&w=500&q=75",
                            price_from=120, duration="2 soat", order=6),
            ])
            self.stdout.write(self.style.SUCCESS("Yo'nalishlar qo'shildi (6 ta)."))

        if not Tour.objects.exists():
            Tour.objects.bulk_create([
                Tour(title="Antalya",
                     image_url="https://images.unsplash.com/photo-1689130033348-1ebe2612a3d8?auto=format&fit=crop&w=800&q=75",
                     duration="7 kecha / 8 kun", hotel_label="5* Hotel",
                     price=650, depart_date=datetime.date(2026, 9, 20), return_date=datetime.date(2026, 9, 27),
                     seats_left=3, order=1),
                Tour(title="Maldiv",
                     image_url="https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&w=800&q=75",
                     duration="7 kecha / 8 kun", hotel_label="5* Deluxe",
                     price=1000, depart_date=datetime.date(2026, 9, 25), return_date=datetime.date(2026, 10, 2),
                     seats_left=2, order=2),
                Tour(title="Dubay",
                     image_url="https://images.unsplash.com/photo-1745750434535-5943ef2fd31a?auto=format&fit=crop&w=800&q=75",
                     duration="4 kecha / 5 kun", hotel_label="5* Hotel",
                     price=480, depart_date=datetime.date(2026, 9, 22), return_date=datetime.date(2026, 9, 26),
                     seats_left=5, order=3),
                Tour(title="Sharm El Sheikh",
                     image_url="https://images.unsplash.com/photo-1580058328338-5412e1123bf8?auto=format&fit=crop&w=800&q=75",
                     duration="7 kecha / 8 kun", hotel_label="5* Hotel",
                     price=600, depart_date=datetime.date(2026, 9, 18), return_date=datetime.date(2026, 9, 26),
                     seats_left=4, order=4),
                Tour(title="Istanbul",
                     image_url="https://images.unsplash.com/photo-1763965367191-6455ef032c79?auto=format&fit=crop&w=800&q=75",
                     duration="4 kecha / 5 kun", hotel_label="4* Hotel",
                     price=680, depart_date=datetime.date(2026, 10, 1), return_date=datetime.date(2026, 10, 5),
                     seats_left=6, order=5),
                Tour(title="Batumi",
                     image_url="https://images.unsplash.com/photo-1593544482199-8395682901da?auto=format&fit=crop&w=800&q=75",
                     duration="3 kecha / 4 kun", hotel_label="4* Hotel",
                     price=565, depart_date=datetime.date(2026, 10, 5), return_date=datetime.date(2026, 10, 8),
                     seats_left=8, order=6),
            ])
            self.stdout.write(self.style.SUCCESS("Turlar qo'shildi (6 ta)."))

        if not TourGalleryImage.objects.exists():
            # Tur nomi -> shu shahar uchun Yo'nalishlar bo'limidagi rasm (allaqachon tekshirilgan, ishonchli URL).
            # Bu — 4 tadan rasmning ikkinchisi; admin panelda yana 2 tagacha rasm qo'shish mumkin.
            dest_by_name = {d.name: d for d in Destination.objects.all()}
            tour_to_dest = {
                "Antalya": "Antalya",
                "Maldiv": "Male",
                "Dubay": "Dubay",
                "Sharm El Sheikh": "Sharm El Sheikh",
                "Istanbul": "Istanbul",
                "Batumi": "Batumi",
            }
            gallery = []
            for tour in Tour.objects.all():
                dest_name = tour_to_dest.get(tour.title)
                dest = dest_by_name.get(dest_name)
                if dest and dest.image_url:
                    gallery.append(TourGalleryImage(tour=tour, image_url=dest.image_url, order=1))
            if gallery:
                TourGalleryImage.objects.bulk_create(gallery)
                self.stdout.write(self.style.SUCCESS(
                    f"Tur galereyasiga {len(gallery)} ta rasm qo'shildi (har biriga admin panelda yana 2 tagacha qo'shish mumkin)."
                ))

        if not Testimonial.objects.exists():
            Testimonial.objects.bulk_create([
                Testimonial(name="Dilshoda Karimova", city="Toshkent",
                            avatar_url="https://randomuser.me/api/portraits/women/44.jpg",
                            text="Antalyaga dam olishga bordik, xizmatlar juda zo'r bo'ldi. "
                                 "Hammasi aniq va o'z vaqtida tashkil etilgan. Rahmat Take Avia Trip!"),
                Testimonial(name="Jahongir Norqulov", city="Samarqand",
                            avatar_url="https://randomuser.me/api/portraits/men/32.jpg",
                            text="Dubay safarimiz unutilmas bo'ldi. Ayniqsa, transfer va "
                                 "mehmonxona xizmatidan juda mamnunmiz."),
                Testimonial(name="Sitora Alimova", city="Buxoro",
                            avatar_url="https://randomuser.me/api/portraits/women/68.jpg",
                            text="Maldiv orollari orzumdagi joy edi. Take Avia Trip orqali eng "
                                 "yaxshi narxda borib keldik! Tavsiya qilaman."),
            ])
            self.stdout.write(self.style.SUCCESS("Mijoz fikrlari qo'shildi (3 ta)."))

        # Turlarga uch tildagi SEO-tavsiflarni yozish (alohida buyruqda saqlanadi)
        from django.core.management import call_command
        call_command("seed_descriptions")

        # Mijoz fikrlariga rus/ingliz tarjimalarini yozish (alohida buyruqda saqlanadi)
        call_command("seed_testimonials_i18n")

        self.stdout.write(self.style.SUCCESS("Seed yakunlandi."))
