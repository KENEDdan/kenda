from django.contrib import admin
from .models import SchoolProfile


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('School Identity', {
            'fields': ('name', 'short_name', 'motto',
                       'registration_number', 'school_type')
        }),
        ('Branding', {
            'fields': ('logo', 'primary_color', 'secondary_color')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'phone_alt',
                       'website', 'address', 'city', 'country', 'po_box')
        }),
        ('Academic Settings', {
            'fields': ('school_week_start', 'school_week_end')
        }),
        ('ID Card Settings', {
            'fields': ('id_card_footer', 'id_card_valid_years')
        }),
        ('Reports & Signatures', {
            'fields': ('principal_name', 'principal_signature')
        }),
    )

    def has_add_permission(self, request):
        # Prevent creating more than one profile from admin
        return not SchoolProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False