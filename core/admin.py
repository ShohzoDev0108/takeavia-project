from django.contrib import admin

from .models import Destination, Lead, Testimonial, Tour

admin.site.site_header = "Take Avia Trip — Boshqaruv paneli"
admin.site.site_title = "Take Avia Trip"
admin.site.index_title = "Sayt boshqaruvi"


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "price_from", "duration", "is_popular", "order")
    list_editable = ("price_from", "is_popular", "order")
    search_fields = ("name", "country")


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "dates", "seats_left", "rating", "is_active", "order")
    list_editable = ("price", "seats_left", "is_active", "order")
    search_fields = ("title",)
    list_filter = ("is_active",)


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
    search_fields = ("name", "contact", "from_city", "to_city")
    readonly_fields = ("created_at",)
