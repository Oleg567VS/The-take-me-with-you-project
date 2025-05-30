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
admin.site.register(Shelter)
admin.site.register(ShelterRepresentative)
admin.site.register(Animal)
admin.site.register(Photo)
admin.site.register(Application)
admin.site.register(LostAnimal)
admin.site.register(FoundReport)
admin.site.register(FoundAnimal)

# Register your models here.
