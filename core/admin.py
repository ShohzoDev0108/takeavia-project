from django.contrib import admin
from django.utils.html import format_html

from .models import Destination, Lead, SiteSettings, Testimonial, Tour

admin.site.site_header = "Take Avia Trip — Boshqaruv paneli"
admin.site.site_title = "Take Avia Trip"
admin.site.index_title = "Sayt boshqaruvi"


def _thumb(obj, size=60):
    """Ro'yxatda kichik rasm ko'rinishini chizadi."""
    src = obj.image_src
    if not src:
        return "—"
    return format_html(
        '<img src="{}" style="width:{}px; height:{}px; object-fit:cover; border-radius:6px;">',
        src, size, size,
    )


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("thumb", "__str__", "name", "country", "price_from", "duration", "is_popular", "order")
    list_editable = ("price_from", "is_popular", "order")
    search_fields = ("name", "country", "to_code")
    fields = (
        "name", "country", "flag_code", "from_code", "to_code",
        "image", "image_preview", "image_url",
        "price_from", "duration", "is_popular", "order",
    )
    readonly_fields = ("image_preview",)

    @admin.display(description="Rasm")
    def thumb(self, obj):
        return _thumb(obj)

    @admin.display(description="Joriy rasm")
    def image_preview(self, obj):
        return _thumb(obj, size=160)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        "thumb", "title", "price", "depart_date", "return_date",
        "seats_left", "rating", "is_active", "order",
    )
    list_editable = ("price", "depart_date", "return_date", "seats_left", "is_active", "order")
    search_fields = ("title",)
    list_filter = ("is_active",)
    date_hierarchy = "depart_date"
    fields = (
        "title", "image", "image_preview", "image_url",
        "duration", "hotel_label", "includes", "price",
        "depart_date", "return_date",
        "seats_left", "rating", "is_active", "order",
    )
    readonly_fields = ("image_preview",)

    @admin.display(description="Rasm")
    def thumb(self, obj):
        return _thumb(obj)

    @admin.display(description="Joriy rasm")
    def image_preview(self, obj):
        return _thumb(obj, size=160)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "rating", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "city")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("__str__", "kind", "name", "contact", "tour", "created_at", "is_processed")
    list_editable = ("is_processed",)
    list_filter = ("kind", "is_processed")
    search_fields = ("name", "contact", "from_city", "to_city", "message")
    readonly_fields = ("created_at",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Faqat bitta yozuv bo'ladi — telefon, email, manzil, ish vaqti va xaritadagi joyni shu yerdan tahrirlang."""

    fields = (
        "phone_1", "phone_2", "email_1", "email_2", "address", "working_hours",
        "map_picker", "latitude", "longitude",
        "telegram_url", "instagram_url", "facebook_url", "youtube_url",
    )
    readonly_fields = ("map_picker",)

    class Media:
        css = {"all": ("https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css",)}
        js = ("https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js",)

    def has_add_permission(self, request):
        # Faqat bitta "Sayt sozlamalari" yozuvi bo'lishi kerak.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Ro'yxat sahifasini chetlab o'tib, to'g'ridan-to'g'ri tahrirlash formasiga yo'naltiramiz.
        obj = SiteSettings.load()
        from django.shortcuts import redirect
        from django.urls import reverse

        return redirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))

    @admin.display(description="Xaritadan joyni tanlang (bosing yoki belgini suring)")
    def map_picker(self, obj):
        lat = obj.latitude if obj and obj.pk else 41.318567
        lng = obj.longitude if obj and obj.pk else 69.315329
        return format_html(
            '''
            <div id="site-map-picker" style="height:360px; max-width:640px; border-radius:10px; border:1px solid #ccc;"></div>
            <p style="margin-top:6px; color:#666; font-size:12.5px;">
                Xaritani bosing yoki belgini sudrab, aniq manzilni tanlang — koordinatalar pastdagi
                maydonlarga avtomatik yoziladi.
            </p>
            <script>
              (function() {{
                var tries = 0;
                function initSiteMap() {{
                  tries++;
                  if (typeof L === 'undefined') {{
                    if (tries < 40) {{ setTimeout(initSiteMap, 150); }}
                    return;
                  }}
                  var latInput = document.getElementById('id_latitude');
                  var lngInput = document.getElementById('id_longitude');
                  var startLat = parseFloat(latInput.value) || {lat};
                  var startLng = parseFloat(lngInput.value) || {lng};
                  var map = L.map('site-map-picker').setView([startLat, startLng], 15);
                  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap',
                    maxZoom: 19,
                  }}).addTo(map);
                  var marker = L.marker([startLat, startLng], {{draggable: true}}).addTo(map);
                  function updateFields(latlng) {{
                    latInput.value = latlng.lat.toFixed(6);
                    lngInput.value = latlng.lng.toFixed(6);
                  }}
                  marker.on('dragend', function() {{ updateFields(marker.getLatLng()); }});
                  map.on('click', function(e) {{
                    marker.setLatLng(e.latlng);
                    updateFields(e.latlng);
                  }});
                  // Admin forma ichida xarita ba'zan noto'g'ri o'lchamda chiziladi — bir necha marta qayta o'lchaymiz.
                  setTimeout(function() {{ map.invalidateSize(); }}, 300);
                  setTimeout(function() {{ map.invalidateSize(); }}, 900);
                }}
                if (document.readyState === 'loading') {{
                  document.addEventListener('DOMContentLoaded', initSiteMap);
                }} else {{
                  initSiteMap();
                }}
              }})();
            </script>
            ''',
            lat=lat, lng=lng,
        )
