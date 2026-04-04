from django.db import models


class SchoolProfile(models.Model):
    """
    Singleton model — only one record ever exists.
    Stores all school-level branding and contact info.
    """

    class DayChoices(models.TextChoices):
        MONDAY = 'monday', 'Monday'
        TUESDAY = 'tuesday', 'Tuesday'
        WEDNESDAY = 'wednesday', 'Wednesday'
        THURSDAY = 'thursday', 'Thursday'
        FRIDAY = 'friday', 'Friday'
        SATURDAY = 'saturday', 'Saturday'
        SUNDAY = 'sunday', 'Sunday'

    # Identity
    name = models.CharField(max_length=200, default='My School')
    short_name = models.CharField(max_length=50, blank=True)
    motto = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)

    # Branding
    logo = models.ImageField(upload_to='school/logo/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#2D1B69', blank=True)
    secondary_color = models.CharField(max_length=7, default='#F59E0B', blank=True)

    # Contact
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    phone_alt = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Rwanda')
    po_box = models.CharField(max_length=50, blank=True)

    # Academic settings
    school_type = models.CharField(
        max_length=50,
        choices=[
            ('primary', 'Primary School'),
            ('secondary', 'Secondary School'),
            ('combined', 'Combined School'),
            ('university', 'University / College'),
            ('vocational', 'Vocational Institute'),
        ],
        default='combined'
    )
    school_week_start = models.CharField(
        max_length=10, choices=DayChoices.choices, default='monday'
    )
    school_week_end = models.CharField(
        max_length=10, choices=DayChoices.choices, default='friday'
    )

    # ID Card
    id_card_footer = models.CharField(
        max_length=200,
        default="If found please return to school office",
        blank=True
    )
    id_card_show_photo = models.BooleanField(default=True)
    id_card_valid_years = models.PositiveIntegerField(
        default=1,
        help_text="Number of years the ID card is valid"
    )
    registration_number = models.CharField(
        max_length=100, blank=True,
        help_text="Official school registration number"
    )
    
    # Report settings
    principal_name = models.CharField(max_length=200, blank=True)
    principal_signature = models.ImageField(
        upload_to='school/signatures/', null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'School Profile'
        verbose_name_plural = 'School Profile'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj