from django.core.management.base import BaseCommand

from core.models import Destination, Testimonial, Tour


class Command(BaseCommand):
    help = "Saytni boshlang'ich ma'lumotlar bilan to'ldiradi (mavjudlarini o'chirmaydi)."

    def handle(self, *args, **options):
        if not Destination.objects.exists():
            Destination.objects.bulk_create([
                Destination(name="Antalya", country="Turkiya", flag_code="tr",
                            image_url="https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=500&q=75",
                            price_from=520, duration="7 kecha / 8 kun", is_popular=True, order=1),
                Destination(name="Maldiv", country="Mahar orollari", flag_code="mv",
                            image_url="https://images.unsplash.com/photo-1573843981267-be1999ff37cd?auto=format&fit=crop&w=500&q=75",
                            price_from=910, duration="7 kecha / 8 kun", order=2),
                Destination(name="Dubay", country="BAA", flag_code="ae",
                            image_url="https://images.unsplash.com/photo-1512632578888-169bbbc64f33?auto=format&fit=crop&w=500&q=75",
                            price_from=470, duration="5 kecha / 6 kun", order=3),
                Destination(name="Istanbul", country="Turkiya", flag_code="tr",
                            image_url="https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=500&q=75",
                            price_from=450, duration="4 kecha / 5 kun", order=4),
                Destination(name="Sharm El Sheikh", country="Misr", flag_code="eg",
                            image_url="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=500&q=75",
                            price_from=480, duration="7 kecha / 8 kun", order=5),
                Destination(name="Batumi", country="Gruziya", flag_code="ge",
                            image_url="https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=500&q=75",
                            price_from=260, duration="3 kecha / 4 kun", order=6),
            ])
            self.stdout.write(self.style.SUCCESS("Yo'nalishlar qo'shildi (6 ta)."))

        if not Tour.objects.exists():
            Tour.objects.bulk_create([
                Tour(title="Antalya",
                     image_url="https://images.unsplash.com/photo-1590523278191-995cbcda646b?auto=format&fit=crop&w=800&q=75",
                     duration="7 kecha / 8 kun", hotel_label="5* Hotel",
                     price=635, dates="20 – 27 May", seats_left=3, order=1),
                Tour(title="Maldiv",
                     image_url="https://images.unsplash.com/photo-1540202404-1b927e27fa8b?auto=format&fit=crop&w=800&q=75",
                     duration="7 kecha / 8 kun", hotel_label="5* Deluxe",
                     price=995, dates="25 May – 01 Iyun", seats_left=2, order=2),
                Tour(title="Dubay",
                     image_url="https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=800&q=75",
                     duration="4 kecha / 5 kun", hotel_label="5* Hotel",
                     price=560, dates="22 – 26 May", seats_left=5, order=3),
                Tour(title="Sharm El Sheikh",
                     image_url="https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=800&q=75",
                     duration="7 kecha / 8 kun", hotel_label="5* Hotel",
                     price=520, dates="18 – 26 May", seats_left=4, order=4),
                Tour(title="Istanbul",
                     image_url="https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=800&q=75",
                     duration="4 kecha / 5 kun", hotel_label="4* Hotel",
                     price=450, dates="01 – 05 Iyun", seats_left=6, order=5),
                Tour(title="Batumi",
                     image_url="https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=75",
                     duration="3 kecha / 4 kun", hotel_label="4* Hotel",
                     price=260, dates="05 – 08 Iyun", seats_left=8, order=6),
            ])
            self.stdout.write(self.style.SUCCESS("Turlar qo'shildi (6 ta)."))

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

        self.stdout.write(self.style.SUCCESS("Seed yakunlandi."))
