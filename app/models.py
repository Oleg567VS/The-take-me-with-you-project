from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    telephone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    address = models.TextField("Адрес", blank=True, null=True)
    # другие пользовательские поля

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class AdminSite(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    admin_name = models.CharField("Имя администратора", max_length=150)
    telephone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)

    def __str__(self):
        return self.admin_name or self.user.username

    class Meta:
        verbose_name = "Администратор сайта"
        verbose_name_plural = "Администраторы сайта"

class Shelter(models.Model):
    name_shelter = models.CharField("Название приюта", max_length=255)
    address_shelter = models.TextField("Адрес приюта")
    email_shelter = models.EmailField("Email приюта", blank=True, null=True)
    telephone_shelter = models.CharField("Телефон приюта", max_length=20, blank=True, null=True)
    capacity = models.PositiveIntegerField("Вместимость")

    def __str__(self):
        return self.name_shelter

    class Meta:
        verbose_name = "Приют"
        verbose_name_plural = "Приюты"

class ShelterRepresentative(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shelter_representative_profile')
    name = models.CharField("Имя представителя", max_length=150)
    telephone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    shelter = models.OneToOneField('Shelter', on_delete=models.SET_NULL, null=True, related_name='representative_link')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Представитель приюта"
        verbose_name_plural = "Представители приютов"

GENDER_CHOICES = [
    ('male', 'Самец'),
    ('female', 'Самка'),
]

class Animal(models.Model):
    nickname_pets = models.CharField("Кличка", max_length=150)
    breed = models.CharField("Порода", max_length=100)
    age = models.PositiveIntegerField("Возраст")
    view = models.CharField("Вид", max_length=100)
    gender = models.CharField("Пол", max_length=10, choices=GENDER_CHOICES)
    color = models.CharField("Окрас", max_length=100)
    info = models.TextField("Информация о животном", blank=True, null=True)
    shelter = models.ForeignKey('Shelter', on_delete=models.CASCADE, verbose_name="Приют")

    def __str__(self):
        return self.nickname_pets

    class Meta:
        verbose_name = "Животное"
        verbose_name_plural = "Животные"

class Photo(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='photos', verbose_name="Животное")
    image = models.ImageField("Фото", upload_to='animals/')
    is_main = models.BooleanField("Главное фото", default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото {self.animal.nickname_pets}"

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

STATUS_CHOICES = [
    ('pending', 'Ожидает'),
    ('approved', 'Одобрено'),
    ('rejected', 'Отклонено'),
    ('completed', 'Завершено'),
]

class Application(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, verbose_name="Животное")
    status = models.CharField("Статус заявки", max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField("Дата подачи", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    is_completed = models.BooleanField("Усыновлено", default=False)

    def __str__(self):
        return f"{self.user.username} → {self.animal.nickname_pets} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Заявка на усыновление"
        verbose_name_plural = "Заявки на усыновление"

class LostAnimal(models.Model):
    lostie_name = models.CharField("Кличка", max_length=150)
    view = models.CharField("Вид", max_length=100)
    breed = models.CharField("Порода", max_length=100, blank=True, null=True)
    gender = models.CharField("Пол", max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    color = models.CharField("Окрас", max_length=100, blank=True, null=True)
    place_of_loss = models.TextField("Место пропажи")
    date_of_loss = models.DateField("Дата пропажи", default=timezone.now)
    info = models.TextField("Дополнительная информация", blank=True, null=True)
    reward = models.PositiveIntegerField("Награда (руб.)", blank=True, null=True)
    is_urgent = models.BooleanField("Срочно", default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    photo = models.ImageField("Фото животного", upload_to='lost_animals/', blank=True, null=True)
    date_reported = models.DateTimeField("Дата подачи объявления", auto_now_add=True)
    is_found = models.BooleanField("Найдено", default=False)

    def __str__(self):
        return f"{self.lostie_name} ({self.owner.username})"

    class Meta:
        verbose_name = "Потерянное животное"
        verbose_name_plural = "Потерянные животные"

class FoundReport(models.Model):
    losties = models.ForeignKey('LostAnimal', on_delete=models.CASCADE, verbose_name="Потерянное животное")
    the_finder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Нашёл")
    place_found = models.TextField("Место находки", blank=True, null=True)
    date_found = models.DateField("Дата находки", default=timezone.now)
    photo = models.ImageField("Фото", upload_to='found_reports/', blank=True, null=True)
    is_confirmed = models.BooleanField("Подтверждено", default=False)
    confirmed_at = models.DateTimeField("Дата подтверждения", blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"{self.losties.lostie_name} найден пользователем {self.the_finder.username}"

    class Meta:
        verbose_name = "Запись о находке"
        verbose_name_plural = "Записи о находках"

class FoundAnimal(models.Model):
    name = models.CharField("Кличка", max_length=150, blank=True, null=True)
    view = models.CharField("Вид", max_length=100)
    breed = models.CharField("Порода", max_length=100, blank=True, null=True)
    gender = models.CharField("Пол", max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    color = models.CharField("Окрас", max_length=100, blank=True, null=True)
    place_found = models.TextField("Место находки")
    date_found = models.DateField("Дата находки", default=timezone.now)
    finder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Нашёл", related_name='found_animals')
    photo = models.ImageField("Фото", upload_to='found_animals/', blank=True, null=True)
    info = models.TextField("Дополнительная информация", blank=True, null=True)
    is_matched = models.BooleanField("Совпадение найдено", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Без клички'} ({self.view}), найден {self.finder.username}"

    class Meta:
        verbose_name = "Найденное животное"
        verbose_name_plural = "Найденные животные"