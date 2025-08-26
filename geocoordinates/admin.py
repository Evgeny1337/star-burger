from django.contrib import admin
from .models import PlaceCoordinates

@admin.register(PlaceCoordinates)
class PlaceCoordinatesAdmin(admin.ModelAdmin):
    list_display = ('address', 'lat', 'lon', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('address',)
    readonly_fields = ('updated_at',)
