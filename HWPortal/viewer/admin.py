from django.contrib import admin
from .models import (
    Sockets, BoardFormats, RamTypes, StorageTypes,
    Processors, Motherboards, Ram, GraphicsCards, Storage, PowerSupplyUnits,
    Reviews, ReviewVotes
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

@admin.register(StorageTypes)
class StorageTypesAdmin(admin.ModelAdmin):
    list_display = ['type']
    search_fields = ['type']
    ordering = ['type']

@admin.register(Processors)
class ProcessorsAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'socket', 'tdp', 'corecount', 'price', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'socket', 'smt', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['price', 'rating']
    readonly_fields = ['dateadded']
    ordering = ['manufacturer', 'name']
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
    list_display = ['name', 'manufacturer', 'format', 'socket', 'maxcputdp', 'price', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'format', 'socket', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['price', 'rating']
    readonly_fields = ['dateadded']
    ordering = ['manufacturer', 'name']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'manufacturer', 'format', 'socket')
        }),
        ('Technické specifikace', {
            'fields': ('maxcputdp', 'satacount', 'nvmecount', 'pciegen')
        }),
        ('Ekonomické údaje', {
            'fields': ('price', 'rating', 'dateadded')
        }),
    )

@admin.register(Ram)
class RamAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'type', 'capacity', 'clock', 'price', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'type', 'capacity', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['price', 'rating']
    readonly_fields = ['dateadded']
    ordering = ['manufacturer', 'name']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'manufacturer', 'type')
        }),
        ('Technické specifikace', {
            'fields': ('capacity', 'clock')
        }),
        ('Ekonomické údaje', {
            'fields': ('price', 'rating', 'dateadded')
        }),
    )

@admin.register(GraphicsCards)
class GraphicsCardsAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'vram', 'tgp', 'price', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'vram', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['price', 'rating']
    readonly_fields = ['dateadded']
    ordering = ['manufacturer', 'name']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'manufacturer')
        }),
        ('Technické specifikace', {
            'fields': ('vram', 'tgp')
        }),
        ('Ekonomické údaje', {
            'fields': ('price', 'rating', 'dateadded')
        }),
    )

@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'capacity', 'type', 'price', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'type', 'capacity', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['price', 'rating']
    readonly_fields = ['dateadded']
    ordering = ['manufacturer', 'name']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'manufacturer', 'type')
        }),
        ('Technické specifikace', {
            'fields': ('capacity',)
        }),
        ('Ekonomické údaje', {
            'fields': ('price', 'rating', 'dateadded')
        }),
    )

@admin.register(PowerSupplyUnits)
class PowerSupplyUnitsAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'maxpower', 'price', 'rating', 'dateadded']
    list_filter = ['manufacturer', 'maxpower', 'dateadded']
    search_fields = ['name', 'manufacturer']
    list_editable = ['price', 'rating']
    readonly_fields = ['dateadded']
    ordering = ['manufacturer', 'name']
    fieldsets = (
        ('Základní informace', {
            'fields': ('name', 'manufacturer')
        }),
        ('Technické specifikace', {
            'fields': ('maxpower',)
        }),
        ('Ekonomické údaje', {
            'fields': ('price', 'rating', 'dateadded')
        }),
    )

class ReviewVotesInline(admin.TabularInline):
    model = ReviewVotes
    extra = 0
    readonly_fields = ['user', 'is_helpful', 'date_voted']
    can_delete = True

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'reviewer_name', 'author', 'component_type', 'component_name',
        'rating', 'helpful_votes', 'total_votes', 'is_published', 'date_created'
    ]
    list_filter = [
        'component_type', 'rating', 'is_published', 'date_created', 'author'
    ]
    search_fields = ['title', 'reviewer_name', 'content', 'author__username']
    list_editable = ['is_published', 'rating']
    readonly_fields = ['date_created', 'date_updated', 'helpful_votes', 'total_votes', 'component_name']
    inlines = [ReviewVotesInline]
    date_hierarchy = 'date_created'
    ordering = ['-date_created']

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
                      'graphics_card', 'storage', 'power_supply'),
            'description': 'Vyberte typ komponenty a poté konkrétní komponentu'
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
                if field != obj.component_type:
                    if field in form.base_fields:
                        form.base_fields[field].widget.attrs['style'] = 'display: none;'
        return form

@admin.register(ReviewVotes)
class ReviewVotesAdmin(admin.ModelAdmin):
    list_display = ['review_title', 'user', 'is_helpful', 'date_voted']
    list_filter = ['is_helpful', 'date_voted', 'review__component_type']
    search_fields = ['review__title', 'user__username', 'review__reviewer_name']
    readonly_fields = ['date_voted']
    date_hierarchy = 'date_voted'
    ordering = ['-date_voted']

    def review_title(self, obj):
        """Zobrazí název recenze místo celého objektu"""
        return obj.review.title
    review_title.short_description = 'Recenze'
    review_title.admin_order_field = 'review__title'

admin.site.site_header = "Hardware Portal Admin"
admin.site.site_title = "Hardware Portal Admin"
admin.site.index_title = "Správa Hardware Portal"

def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)
make_published.short_description = "Označit vybrané recenze jako publikované"

def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)
make_unpublished.short_description = "Označit vybrané recenze jako nepublikované"

ReviewsAdmin.actions = [make_published, make_unpublished]