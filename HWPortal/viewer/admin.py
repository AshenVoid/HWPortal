from django.contrib import admin
from .models import (
    Sockets, BoardFormats, RamTypes, Processors, Motherboards,
    Ram, GraphicsCards, Storage, PowerSupplyUnits, Reviews, ReviewVotes
)
# Register your models here.

@admin.register(Sockets)
class SocketAdmin(admin.ModelAdmin):
    list_display = ['type']
    search_fields = ['type']

@admin.register(BoardFormats)
class BoardFormatsAdmin(admin.ModelAdmin):
    list_display = ['format']
    search_fields = ['format']

@admin.register(RamTypes)
class RamTypesAdmin(admin.ModelAdmin):
    list_display = ['type']
    search_fields = ['type']

@admin.register(Processors)
class ProcessorsAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'socket', 'tdp', 'corecount', 'price', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'socket', 'smt', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['price', 'rating']
    readonly_fields = ['dateadded']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'manufacturer', 'socket')
        }),
        ('Technické specifikace', {
            'fields': ('tdp', 'corecount', 'smt', 'clock', 'benchresult')
        }),
        ('Ekonomické údaje', {
            'fields': ('price', 'rating', 'dateadded')
        }),
    )

@admin.register(Motherboards)
class MotherboardsAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'format', 'socket', 'maxcputdp', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'format', 'socket', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['rating']
    readonly_fields = ['dateadded']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'manufacturer', 'format', 'socket')
        }),
        ('Technické specifikace', {
            'fields': ('maxcputdp', 'satacount', 'nvmecount', 'pciegen')
        }),
        ('Hodnocení', {
            'fields': ('rating', 'dateadded')
        }),
    )

@admin.register(Ram)
class RamAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'type', 'capacity', 'clock', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'type', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['rating']
    readonly_fields = ['dateadded']

@admin.register(GraphicsCards)
class GraphicsCardsAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'vram', 'tgp', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['rating']
    readonly_fields = ['dateadded']

@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'capacity', 'type', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'type', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['rating']
    readonly_fields = ['dateadded']

@admin.register(PowerSupplyUnits)
class PowerSupplyUnitsAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'maxpower', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['rating']
    readonly_fields = ['dateadded']


class ReviewVotesInline(admin.TabularInline):
    model = ReviewVotes
    extra = 0
    readonly_fields = ['user', 'is_helpful', 'date_voted']

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'reviewer_name', 'component_type', 'component_name',
        'rating', 'helpful_votes', 'is_published', 'date_created'
    ]
    list_filter = [
        'component_type', 'rating', 'is_published', 'date_created'
    ]
    search_fields = ['title', 'reviewer_name', 'content']
    list_editable = ['is_published', 'rating']
    readonly_fields = ['date_created', 'date_updated', 'helpful_votes', 'total_votes']
    inlines = [ReviewVotesInline]

    fieldsets = (
        ('Základní informace', {
            'fields': ('title', 'author', 'reviewer_name', 'is_published')
        }),
        ('Obsah recenze', {
            'fields': ('summary', 'content', 'rating')
        }),
        ('Klady a zápory', {
            'fields': ('pros', 'cons'),
            'classes': ('collapse',)
        }),
        ('Komponenta', {
            'fields': ('component_type', 'processor', 'motherboard', 'ram',
                      'graphics_card', 'storage', 'power_supply')
        }),
        ('Statistiky', {
            'fields': ('helpful_votes', 'total_votes', 'date_created', 'date_updated'),
            'classes': ('collapse',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            component_fields = ['processor', 'motherboard', 'ram', 'graphics_card', 'storage', 'power_supply']
            for field in component_fields:
                if field != obj.component_type.replace('_', ''):
                    if field in form.base_fields:
                        form.base_fields[field].widget.attrs['style'] = 'display: none;'
        return form

@admin.register(ReviewVotes)
class ReviewVotesAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'is_helpful', 'date_voted']
    list_filter = ['is_helpful', 'date_voted']
    search_fields = ['review__title', 'user__username']
    readonly_fields = ['date_voted']

admin.site.site_header = "Hardware Portal Admin"
admin.site.site_title = "Hardware Portal Admin"
admin.site.index_title = "Správa Hardware Portal"


