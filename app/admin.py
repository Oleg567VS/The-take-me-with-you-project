from django.contrib import admin
from .models import (
    AdminSite,
    CustomUser,
    Shelter,
    ShelterRepresentative,
    Animal,
    Photo,
    Application,
    LostAnimal,
    FoundReport,
    FoundAnimal,
)

# Регистрация моделей
admin.site.register(AdminSite)
admin.site.register(CustomUser)

class ShelterAdmin(admin.ModelAdmin):
    list_display = ("name_shelter", "address_shelter", "email_shelter", "telephone_shelter", "capacity", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("name_shelter", "address_shelter", "email_shelter", "telephone_shelter")

admin.site.register(Shelter, ShelterAdmin)

admin.site.register(ShelterRepresentative)
admin.site.register(Animal)
admin.site.register(Photo)
admin.site.register(Application)
admin.site.register(LostAnimal)
admin.site.register(FoundReport)
admin.site.register(FoundAnimal)

# Register your models here.
