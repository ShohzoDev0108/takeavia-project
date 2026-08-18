"""
Turlar uchun uch tildagi SEO-tavsiflarni bazaga yozadi.

Ishlatish (serverda ham, lokalda ham):
    python manage.py seed_descriptions

Xavfsiz: faqat tavsifi BO'SH bo'lgan turlarni to'ldiradi — admin panelda
qo'lda yozilgan matnlarni hech qachon ustidan yozmaydi.
Hammasini majburan yangilash uchun:  python manage.py seed_descriptions --force
"""

from django.core.management.base import BaseCommand

from core.models import Tour

# title -> (uz, ru, en). Xatboshilar \n\n bilan ajratiladi.
DESCRIPTIONS = {
    "Antalya": (
        "Antalya — O'rta yer dengizi bo'yidagi Turkiyaning eng mashhur kurorti. "
        "Toshkentdan to'g'ridan-to'g'ri parvoz bilan bor-yo'g'i 4 soatda yetib borasiz. "
        "Iyun'dan oktabrgacha dengiz suvi cho'milish uchun ideal, qumli va toshli plyajlar, "
        "suv attraksionlari va bolalar uchun ko'ngilochar maskanlar mavsum davomida ishlaydi.\n\n"
        "Tur paketga Toshkent — Antalya — Toshkent aviabileti, 5 yulduzli mehmonxonada "
        "joylashuv, aeroport transferi va sug'urta kiradi. Ko'pchilik mehmonxonalar "
        "\"hammasi narxga kiritilgan\" (all inclusive) tizimida ishlaydi. Turkiya O'zbekiston "
        "fuqarolari uchun vizasiz — faqat pasport yetarli.\n\n"
        "Antalyada Kaleichi eski shahri, Duden sharsharasi, Aspendos amfiteatri va "
        "aquaparklarni ko'rishni tavsiya qilamiz. Aniq sana va narxni bilish uchun "
        "so'rov qoldiring — menejerlarimiz 24/7 xizmatingizda.",

        "Анталья — самый популярный курорт Турции на берегу Средиземного моря. "
        "Прямой перелёт из Ташкента занимает всего 4 часа. С июня по октябрь море "
        "идеально для купания, работают песчаные и галечные пляжи, аквапарки и "
        "развлечения для детей.\n\n"
        "В тур-пакет входят авиабилеты Ташкент — Анталья — Ташкент, проживание в "
        "отеле 5*, трансфер из аэропорта и страховка. Большинство отелей работают "
        "по системе \"всё включено\". Турция безвизовая для граждан Узбекистана — "
        "достаточно загранпаспорта.\n\n"
        "В Анталье рекомендуем посетить старый город Калеичи, водопад Дюден, "
        "амфитеатр Аспендос и аквапарки. Оставьте заявку — наши менеджеры на связи 24/7.",

        "Antalya is Turkey's most popular resort on the Mediterranean coast. "
        "A direct flight from Tashkent takes only 4 hours. From June to October the "
        "sea is perfect for swimming, with sandy and pebble beaches, water parks and "
        "family entertainment.\n\n"
        "The package includes Tashkent — Antalya — Tashkent flights, a 5-star hotel, "
        "airport transfer and insurance. Most hotels operate on an all-inclusive basis. "
        "Turkey is visa-free for citizens of Uzbekistan — a passport is enough.\n\n"
        "We recommend visiting the Kaleici old town, Duden waterfall, the Aspendos "
        "amphitheatre and the water parks. Leave a request — our managers are available 24/7.",
    ),
    "Maldiv": (
        "Maldiv orollari — Hind okeanidagi jannat: oppoq qumli plyajlar, shaffof "
        "feruza suv va suv ustidagi bungalolar. Bu yo'nalish asal oyi va unutilmas "
        "dam olish uchun eng ko'p tanlanadigan manzillardan biri.\n\n"
        "Tur paketga aviabilet (ko'chish bilan, yo'l ~9 soat), 5 yulduzli deluxe "
        "mehmonxona, transfer (katerda yoki gidrosamolyotda) va sug'urta kiradi. "
        "Maldiv O'zbekiston fuqarolari uchun vizasiz — kelganda bepul muhr qo'yiladi.\n\n"
        "Snorkeling va dayving ixlosmandlari uchun marjon riflari, delfinlar bilan "
        "suzish va okean ustida quyosh botishini tomosha qilish — bularning barchasi "
        "sizni kutmoqda. Joylar cheklangan, oldindan band qilishni tavsiya qilamiz.",

        "Мальдивы — рай в Индийском океане: белоснежные пляжи, прозрачная бирюзовая "
        "вода и бунгало над водой. Одно из самых популярных направлений для медового "
        "месяца и незабываемого отдыха.\n\n"
        "В пакет входят авиабилеты (с пересадкой, в пути ~9 часов), отель 5* делюкс, "
        "трансфер (катер или гидросамолёт) и страховка. Мальдивы безвизовые для "
        "граждан Узбекистана — штамп ставится бесплатно по прилёту.\n\n"
        "Коралловые рифы для снорклинга и дайвинга, плавание с дельфинами и закаты "
        "над океаном — всё это ждёт вас. Количество мест ограничено, рекомендуем "
        "бронировать заранее.",

        "The Maldives is a paradise in the Indian Ocean: white sandy beaches, "
        "crystal-clear turquoise water and overwater bungalows. One of the most "
        "popular destinations for honeymoons and unforgettable holidays.\n\n"
        "The package includes flights (with a layover, ~9 hours total), a 5-star "
        "deluxe hotel, transfer (speedboat or seaplane) and insurance. The Maldives "
        "is visa-free for citizens of Uzbekistan — a free stamp is issued on arrival.\n\n"
        "Coral reefs for snorkelling and diving, swimming with dolphins and ocean "
        "sunsets await you. Seats are limited — we recommend booking in advance.",
    ),
    "Dubay": (
        "Dubay — zamonaviy arxitektura, cheksiz savdo markazlari va yil bo'yi quyosh "
        "shahri. Toshkentdan parvoz atigi 2 soat 40 daqiqa — eng yaqin \"katta\" "
        "xorijiy kurortlardan biri.\n\n"
        "Tur paketga aviabilet, 5 yulduzli mehmonxona, transfer va sug'urta kiradi. "
        "BAA O'zbekiston fuqarolari uchun vizasiz. Burj Khalifa, Dubai Mall, Palm "
        "Jumeirah oroli, cho'l safarisi va Dubai Fountain shousi — 4-5 kunlik dastur "
        "uchun yetarli taassurot.\n\n"
        "Noyabrdan aprelgacha ob-havo dam olish uchun eng qulay (25–30°C). Oilaviy "
        "sayohat, shopping yoki ish safari — Dubay har qanday maqsadga mos keladi.",

        "Дубай — город современной архитектуры, бесконечных торговых центров и "
        "круглогодичного солнца. Перелёт из Ташкента занимает всего 2 часа 40 минут — "
        "один из ближайших \"больших\" зарубежных курортов.\n\n"
        "В пакет входят авиабилеты, отель 5*, трансфер и страховка. ОАЭ безвизовые "
        "для граждан Узбекистана. Бурдж-Халифа, Dubai Mall, остров Пальма Джумейра, "
        "сафари по пустыне и шоу фонтанов — впечатлений хватит на 4-5 дней.\n\n"
        "С ноября по апрель погода самая комфортная (25–30°C). Семейный отдых, "
        "шопинг или деловая поездка — Дубай подходит для любых целей.",

        "Dubai is a city of modern architecture, endless shopping malls and "
        "year-round sunshine. The flight from Tashkent takes only 2 hours 40 minutes — "
        "one of the closest major resort destinations.\n\n"
        "The package includes flights, a 5-star hotel, transfer and insurance. The UAE "
        "is visa-free for citizens of Uzbekistan. Burj Khalifa, Dubai Mall, Palm "
        "Jumeirah, desert safari and the fountain show — enough impressions for a "
        "4-5 day trip.\n\n"
        "From November to April the weather is at its best (25–30°C). Family holiday, "
        "shopping or business trip — Dubai suits any purpose.",
    ),
    "Sharm El Sheikh": (
        "Sharm El Sheikh — Misrning Qizil dengiz bo'yidagi kurorti, yil bo'yi "
        "cho'milish mavsumi va dunyodagi eng go'zal marjon riflaridan biri. "
        "Parvoz Toshkentdan ~5 soat 30 daqiqa.\n\n"
        "Tur paketga aviabilet, 5 yulduzli mehmonxona (aksariyati all inclusive), "
        "transfer va sug'urta kiradi. Misr vizasi O'zbekiston fuqarolari uchun "
        "aeroportda oson rasmiylashtiriladi — hujjatlarda o'zimiz yordam beramiz.\n\n"
        "Ras Muhammad milliy bog'ida snorkeling, Naama Bay ko'ngilochar markazi, "
        "cho'lda kvadrotsikl safari va Sinay tog'iga sayohat — Sharm hech kimni "
        "befarq qoldirmaydi. Qishda ham dengiz suvi +22°C dan tushmaydi.",

        "Шарм-эль-Шейх — курорт Египта на Красном море с круглогодичным купальным "
        "сезоном и одними из красивейших коралловых рифов мира. Перелёт из Ташкента "
        "~5 часов 30 минут.\n\n"
        "В пакет входят авиабилеты, отель 5* (большинство — всё включено), трансфер "
        "и страховка. Египетская виза для граждан Узбекистана легко оформляется в "
        "аэропорту — с документами поможем.\n\n"
        "Снорклинг в национальном парке Рас-Мохаммед, развлечения Наама-Бей, сафари "
        "на квадроциклах и поездка на гору Синай — Шарм никого не оставит равнодушным. "
        "Даже зимой вода не опускается ниже +22°C.",

        "Sharm El Sheikh is Egypt's Red Sea resort with a year-round swimming season "
        "and some of the most beautiful coral reefs in the world. The flight from "
        "Tashkent takes ~5.5 hours.\n\n"
        "The package includes flights, a 5-star hotel (mostly all-inclusive), transfer "
        "and insurance. The Egyptian visa is easily issued at the airport for citizens "
        "of Uzbekistan — we help with the paperwork.\n\n"
        "Snorkelling in Ras Mohammed national park, Naama Bay entertainment, quad "
        "safaris in the desert and a trip to Mount Sinai — Sharm leaves no one "
        "indifferent. Even in winter the water stays above +22°C.",
    ),
    "Istanbul": (
        "Istanbul — ikki qit'ada joylashgan yagona shahar: Yevropa va Osiyo "
        "madaniyatining uyg'unligi, ming yillik tarix va mashhur turk oshxonasi. "
        "Toshkentdan to'g'ridan-to'g'ri parvoz ~5 soat.\n\n"
        "Tur paketga aviabilet, markazdagi 4 yulduzli mehmonxona, transfer va "
        "sug'urta kiradi. Turkiya O'zbekiston fuqarolari uchun vizasiz.\n\n"
        "Ayasofya, Ko'k masjid, Topqopi saroyi, Bosfor bo'ylab kema sayri va Grand "
        "Bazaar — 4-5 kunlik shahar sayohati uchun ideal dastur. Istanbul yil "
        "bo'yi go'zal: bahor va kuzda ob-havo ayniqsa yoqimli.",

        "Стамбул — единственный город на двух континентах: сочетание культур Европы "
        "и Азии, тысячелетняя история и знаменитая турецкая кухня. Прямой перелёт из "
        "Ташкента ~5 часов.\n\n"
        "В пакет входят авиабилеты, отель 4* в центре, трансфер и страховка. Турция "
        "безвизовая для граждан Узбекистана.\n\n"
        "Айя-София, Голубая мечеть, дворец Топкапы, круиз по Босфору и Гранд-базар — "
        "идеальная программа городского путешествия на 4-5 дней. Стамбул прекрасен "
        "круглый год, особенно весной и осенью.",

        "Istanbul is the only city on two continents: a blend of European and Asian "
        "cultures, a thousand years of history and famous Turkish cuisine. A direct "
        "flight from Tashkent takes ~5 hours.\n\n"
        "The package includes flights, a 4-star hotel in the centre, transfer and "
        "insurance. Turkey is visa-free for citizens of Uzbekistan.\n\n"
        "Hagia Sophia, the Blue Mosque, Topkapi Palace, a Bosphorus cruise and the "
        "Grand Bazaar — a perfect 4-5 day city break. Istanbul is beautiful all year "
        "round, especially in spring and autumn.",
    ),
    "Batumi": (
        "Batumi — Gruziyaning Qora dengiz bo'yidagi marvaridi: subtropik tabiat, "
        "zamonaviy shahar va mashhur gruzin mehmondo'stligi. Toshkentdan parvoz "
        "atigi ~2 soat — eng yaqin dengiz kurortlaridan biri.\n\n"
        "Tur paketga aviabilet, 4 yulduzli mehmonxona, transfer va sug'urta kiradi. "
        "Gruziya O'zbekiston fuqarolari uchun vizasiz.\n\n"
        "Batumi bulvari, botanika bog'i, Ali va Nino haykali, tungi shahar va albatta "
        "gruzin taomlari — xachapuri, xinkali va mahalliy vino. Iyun-sentabr — dengiz "
        "mavsumi, qolgan oylarda ham shahar sayohati uchun ajoyib manzil.",

        "Батуми — жемчужина Грузии на Чёрном море: субтропическая природа, "
        "современный город и знаменитое грузинское гостеприимство. Перелёт из "
        "Ташкента всего ~2 часа — один из ближайших морских курортов.\n\n"
        "В пакет входят авиабилеты, отель 4*, трансфер и страховка. Грузия "
        "безвизовая для граждан Узбекистана.\n\n"
        "Батумский бульвар, ботанический сад, статуя Али и Нино, ночной город и, "
        "конечно, грузинская кухня — хачапури, хинкали и местное вино. Июнь-сентябрь — "
        "морской сезон, в остальные месяцы — отличное направление для городской поездки.",

        "Batumi is Georgia's pearl on the Black Sea: subtropical nature, a modern "
        "city and famous Georgian hospitality. The flight from Tashkent takes only "
        "~2 hours — one of the closest seaside resorts.\n\n"
        "The package includes flights, a 4-star hotel, transfer and insurance. "
        "Georgia is visa-free for citizens of Uzbekistan.\n\n"
        "Batumi Boulevard, the botanical garden, the Ali and Nino statue, the night "
        "city and of course Georgian cuisine — khachapuri, khinkali and local wine. "
        "June to September is the sea season; the rest of the year it is a great "
        "city-break destination.",
    ),
}


class Command(BaseCommand):
    help = "Turlarga uch tildagi SEO-tavsiflarni yozadi (bo'sh bo'lganlarinigina)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Mavjud tavsiflarni ham ustidan yozish.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        updated = 0
        for title, (uz, ru, en) in DESCRIPTIONS.items():
            for tour in Tour.objects.filter(title=title):
                if tour.description and not force:
                    self.stdout.write(f"O'tkazib yuborildi (tavsifi bor): {title}")
                    continue
                tour.description = uz
                tour.description_ru = ru
                tour.description_en = en
                tour.save(update_fields=["description", "description_ru", "description_en"])
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Tavsif yozildi: {title}"))
        self.stdout.write(self.style.SUCCESS(f"Jami yangilandi: {updated} ta tur."))
