from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Animal, LostAnimal, Shelter, CustomUser, ShelterRepresentative, FoundAnimal, Message
from django.db.models import Q
import re
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone

def index(request):
    return render(request, 'app/index.html')

def home(request):
    # 8 животных из приютов для блока "Возьми меня домой"
    animals = Animal.objects.all()[:8]
    # Все потерянные животные для карты
    lost_animals = list(LostAnimal.objects.filter(is_deleted=False).values('id', 'lostie_name', 'place_of_loss', 'latitude', 'longitude'))
    found_animals = list(FoundAnimal.objects.filter(is_deleted=False).values('id', 'name', 'place_found', 'latitude', 'longitude'))
    return render(request, 'home.html', {
        'animals': animals,
        'lost_animals': lost_animals,
        'found_animals': found_animals,
    })

def register(request):
    shelters = Shelter.objects.all()
    errors = {}
    values = {}
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', '')
        new_name_shelter = request.POST.get('new_name_shelter', '').strip()
        new_address_shelter = request.POST.get('new_address_shelter', '').strip()
        new_email_shelter = request.POST.get('new_email_shelter', '').strip()
        new_telephone_shelter = request.POST.get('new_telephone_shelter', '').strip()
        new_capacity = request.POST.get('new_capacity', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        values = {
            'username': username,
            'email': email,
            'phone': phone,
            'role': role,
            'new_name_shelter': new_name_shelter,
            'new_address_shelter': new_address_shelter,
            'new_email_shelter': new_email_shelter,
            'new_telephone_shelter': new_telephone_shelter,
            'new_capacity': new_capacity,
        }

        # Проверка обязательных полей
        if not username:
            errors['username'] = 'Введите имя пользователя.'
        if not email:
            errors['email'] = 'Введите email.'
        if not phone:
            errors['phone'] = 'Введите телефон.'
        if not password1:
            errors['password1'] = 'Введите пароль.'
        if not password2:
            errors['password2'] = 'Подтвердите пароль.'
        if role == 'shelter':
            if not new_name_shelter:
                errors['new_name_shelter'] = 'Введите название приюта.'
            if not new_address_shelter:
                errors['new_address_shelter'] = 'Введите адрес приюта.'

        # Проверка уникальности username
        if username and CustomUser.objects.filter(username=username).exists():
            errors['username'] = 'Пользователь с таким именем уже существует.'

        # Проверка уникальности email и телефона
        if email and phone and CustomUser.objects.filter(Q(email=email) | Q(telephone=phone)).exists():
            errors['email'] = 'Пользователь с таким email или телефоном уже существует.'
            errors['phone'] = 'Пользователь с таким email или телефоном уже существует.'

        # Проверка совпадения паролей
        if password1 != password2:
            errors['password2'] = 'Пароли не совпадают.'

        # Проверка сложности пароля
        if len(password1) < 8 or not re.search(r'[A-Z]', password1) or not re.search(r'[a-z]', password1) or not re.search(r'\d', password1):
            errors['password1'] = 'Пароль должен быть не менее 8 символов, содержать заглавные и строчные буквы и цифры.'

        if errors:
            return render(request, 'registration/register.html', {'shelters': shelters, 'errors': errors, 'values': values})

        # Создание пользователя
        user = CustomUser.objects.create_user(username=username, email=email, telephone=phone, password=password1)
        user.save()

        # Если представитель приюта — создаём профиль и связываем с приютом
        if role == 'shelter':
            shelter = Shelter.objects.create(
                name_shelter=new_name_shelter,
                address_shelter=new_address_shelter,
                email_shelter=new_email_shelter,
                telephone_shelter=new_telephone_shelter,
                capacity=int(new_capacity) if new_capacity.isdigit() else None,
                is_approved=False
            )
            ShelterRepresentative.objects.create(user=user, name=username, telephone=phone, email=email, shelter=shelter)

        login(request, user)
        return redirect('home')

    return render(request, 'registration/register.html', {'shelters': shelters, 'errors': errors, 'values': values})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'registration/login.html')

@login_required
def add_lost(request):
    shelters = Shelter.objects.all()
    errors = {}
    if request.method == 'POST':
        lostie_name = request.POST.get('lostie_name', '').strip()
        view = request.POST.get('view', '').strip()
        breed = request.POST.get('breed', '').strip()
        color = request.POST.get('color', '').strip()
        place_of_loss = request.POST.get('place_of_loss', '').strip()
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        date_of_loss = request.POST.get('date_of_loss', '').strip()
        info = request.POST.get('info', '').strip()
        # Валидация
        if not lostie_name:
            errors['lostie_name'] = 'Введите кличку.'
        if not view:
            errors['view'] = 'Введите вид.'
        if not place_of_loss:
            errors['place_of_loss'] = 'Укажите место пропажи.'
        if not date_of_loss:
            errors['date_of_loss'] = 'Укажите дату пропажи.'
        # latitude и longitude не обязательны, но если указаны — должны быть числами
        lat_value = None
        lon_value = None
        if latitude:
            try:
                lat_value = float(latitude)
            except ValueError:
                errors['latitude'] = 'Некорректная широта.'
        if longitude:
            try:
                lon_value = float(longitude)
            except ValueError:
                errors['longitude'] = 'Некорректная долгота.'
        if not errors:
            lost_animal = LostAnimal.objects.create(
                lostie_name=lostie_name,
                view=view,
                breed=breed,
                color=color,
                place_of_loss=place_of_loss,
                latitude=lat_value,
                longitude=lon_value,
                date_of_loss=date_of_loss,
                info=info,
                owner=request.user,
                photo=request.FILES.get('photo') if request.FILES.get('photo') else None
            )
            return redirect('home')
    return render(request, 'add_lost.html', {'errors': errors})

@login_required
def add_found(request):
    errors = {}
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        view = request.POST.get('view', '').strip()
        breed = request.POST.get('breed', '').strip()
        color = request.POST.get('color', '').strip()
        place_found = request.POST.get('place_found', '').strip()
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        date_found = request.POST.get('date_found', '').strip()
        info = request.POST.get('info', '').strip()
        # Валидация
        if not view:
            errors['view'] = 'Введите вид.'
        if not place_found:
            errors['place_found'] = 'Укажите место находки.'
        if not date_found:
            errors['date_found'] = 'Укажите дату находки.'
        # latitude и longitude не обязательны, но если указаны — должны быть числами
        lat_value = None
        lon_value = None
        if latitude:
            try:
                lat_value = float(latitude)
            except ValueError:
                errors['latitude'] = 'Некорректная широта.'
        if longitude:
            try:
                lon_value = float(longitude)
            except ValueError:
                errors['longitude'] = 'Некорректная долгота.'
        if not errors:
            found_animal = FoundAnimal.objects.create(
                name=name,
                view=view,
                breed=breed,
                color=color,
                place_found=place_found,
                latitude=lat_value,
                longitude=lon_value,
                date_found=date_found,
                info=info,
                finder=request.user,
                photo=request.FILES.get('photo') if request.FILES.get('photo') else None
            )
            return redirect('home')
    return render(request, 'add_found.html', {'errors': errors})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    shelter_rep = getattr(user, 'shelter_representative_profile', None)
    admin_profile = getattr(user, 'admin_profile', None)
    errors = {}
    success = False
    animals = []
    if shelter_rep and shelter_rep.shelter:
        animals = shelter_rep.shelter.animal_set.all()
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        address = request.POST.get('address', '').strip()
        if not email:
            errors['email'] = 'Email обязателен.'
        if not telephone:
            errors['telephone'] = 'Телефон обязателен.'
        if not errors:
            user.email = email
            user.telephone = telephone
            user.address = address
            user.save()
            success = True
    return render(request, 'profile.html', {
        'user': user,
        'shelter_rep': shelter_rep,
        'admin_profile': admin_profile,
        'errors': errors,
        'success': success,
        'animals': animals,
    })

@login_required
def edit_shelter(request):
    user = request.user
    # Только представитель приюта может редактировать
    shelter_rep = getattr(user, 'shelter_representative_profile', None)
    if not shelter_rep or not shelter_rep.shelter:
        return redirect('profile')
    shelter = shelter_rep.shelter
    errors = {}
    success = False
    if request.method == 'POST':
        name = request.POST.get('name_shelter', '').strip()
        city = request.POST.get('city', '').strip()
        address = request.POST.get('address_shelter', '').strip()
        email = request.POST.get('email_shelter', '').strip()
        telephone = request.POST.get('telephone_shelter', '').strip()
        capacity = request.POST.get('capacity', '').strip()
        if not name:
            errors['name_shelter'] = 'Название обязательно.'
        if not city:
            errors['city'] = 'Город обязателен.'
        if not address:
            errors['address_shelter'] = 'Адрес обязателен.'
        if not errors:
            shelter.name_shelter = name
            shelter.city = city
            shelter.address_shelter = address
            shelter.email_shelter = email
            shelter.telephone_shelter = telephone
            shelter.capacity = int(capacity) if capacity.isdigit() else None
            shelter.save()
            success = True
    return render(request, 'edit_shelter.html', {
        'shelter': shelter,
        'errors': errors,
        'success': success,
    })

@login_required
def add_animal(request):
    user = request.user
    shelter_rep = getattr(user, 'shelter_representative_profile', None)
    if not shelter_rep or not shelter_rep.shelter:
        return redirect('profile')
    shelter = shelter_rep.shelter
    errors = {}
    values = {}
    if not shelter.is_approved:
        errors['shelter'] = 'Ваш приют ещё не подтверждён администратором. Добавление животных недоступно.'
        return render(request, 'add_animal.html', {'errors': errors, 'values': values})
    if request.method == 'POST':
        nickname_pets = request.POST.get('nickname_pets', '').strip()
        breed = request.POST.get('breed', '').strip()
        age = request.POST.get('age', '').strip()
        size = request.POST.get('size', '').strip()
        view = request.POST.get('view', '').strip()
        gender = request.POST.get('gender', '').strip()
        color = request.POST.get('color', '').strip()
        info = request.POST.get('info', '').strip()
        photos = request.FILES.getlist('photo')
        values = {
            'nickname_pets': nickname_pets,
            'breed': breed,
            'age': age,
            'size': size,
            'view': view,
            'gender': gender,
            'color': color,
            'info': info,
        }
        # Валидация
        if not nickname_pets:
            errors['nickname_pets'] = 'Введите кличку.'
        if not age or not age.isdigit():
            errors['age'] = 'Укажите возраст (число).' 
        if not view:
            errors['view'] = 'Введите вид.'
        if not gender:
            errors['gender'] = 'Укажите пол.'
        if not size:
            errors['size'] = 'Укажите размер.'
        if not errors:
            from .models import Animal, Photo
            animal = Animal.objects.create(
                nickname_pets=nickname_pets,
                breed=breed,
                age=int(age),
                size=size,
                view=view,
                gender=gender,
                color=color,
                info=info,
                shelter=shelter
            )
            for i, photo in enumerate(photos):
                Photo.objects.create(animal=animal, image=photo, is_main=(i == 0))
            return redirect('profile')
    return render(request, 'add_animal.html', {'errors': errors, 'values': values})

def animal_detail(request, animal_id):
    animal = Animal.objects.select_related('shelter').prefetch_related('photos').get(id=animal_id)
    photos = animal.photos.all()
    return render(request, 'animal_detail.html', {
        'animal': animal,
        'photos': photos,
    })

def take_animals(request):
    animals = Animal.objects.select_related('shelter').prefetch_related('photos').all()
    # Фильтры
    size = request.GET.get('size')
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    breed = request.GET.get('breed')
    gender = request.GET.get('gender')
    city = request.GET.get('city')
    view_type = request.GET.get('view')
    if size:
        animals = animals.filter(size=size)
    if gender:
        animals = animals.filter(gender=gender)
    if breed:
        animals = animals.filter(breed__icontains=breed)
    if city:
        animals = animals.filter(shelter__city=city)
    if view_type:
        animals = animals.filter(view=view_type)
    if age_min:
        animals = animals.filter(age__gte=age_min)
    if age_max:
        animals = animals.filter(age__lte=age_max)
    # Пагинация
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
        if per_page not in [20, 50, 100]:
            per_page = 20
    except:
        per_page = 20
    paginator = Paginator(animals, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Для фильтров: список пород, городов, видов
    breeds = Animal.objects.values_list('breed', flat=True).distinct()
    cities = Shelter.objects.values_list('city', flat=True).distinct()
    views = Animal.objects.values_list('view', flat=True).distinct()
    return render(request, 'take_animals.html', {
        'page_obj': page_obj,
        'breeds': breeds,
        'cities': cities,
        'views': views,
        'filter': {
            'size': size,
            'age_min': age_min,
            'age_max': age_max,
            'breed': breed,
            'gender': gender,
            'city': city,
            'view': view_type,
            'per_page': per_page,
        }
    })

@login_required
def edit_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    shelter_rep = getattr(request.user, 'shelter_representative_profile', None)
    if not shelter_rep or animal.shelter != shelter_rep.shelter:
        return redirect('profile')
    errors = {}
    if request.method == 'POST':
        nickname_pets = request.POST.get('nickname_pets', '').strip()
        breed = request.POST.get('breed', '').strip()
        age = request.POST.get('age', '').strip()
        size = request.POST.get('size', '').strip()
        view = request.POST.get('view', '').strip()
        gender = request.POST.get('gender', '').strip()
        color = request.POST.get('color', '').strip()
        info = request.POST.get('info', '').strip()
        if not nickname_pets:
            errors['nickname_pets'] = 'Введите кличку.'
        if not age or not age.isdigit():
            errors['age'] = 'Укажите возраст (число).'
        if not view:
            errors['view'] = 'Введите вид.'
        if not gender:
            errors['gender'] = 'Укажите пол.'
        if not size:
            errors['size'] = 'Укажите размер.'
        if not errors:
            animal.nickname_pets = nickname_pets
            animal.breed = breed
            animal.age = int(age)
            animal.size = size
            animal.view = view
            animal.gender = gender
            animal.color = color
            animal.info = info
            animal.save()
            return redirect('profile')
    return render(request, 'edit_animal.html', {'animal': animal, 'errors': errors})

@login_required
def delete_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    shelter_rep = getattr(request.user, 'shelter_representative_profile', None)
    if request.method == 'POST' and shelter_rep and animal.shelter == shelter_rep.shelter:
        animal.delete()
    return redirect('profile')

def lost_found_list(request):
    view_type = request.GET.get('view', '')
    color = request.GET.get('color', '')
    status = request.GET.get('status', 'lost')
    if status == 'found':
        queryset = FoundAnimal.objects.filter(is_deleted=False)
        name_field = 'name'
    else:
        queryset = LostAnimal.objects.filter(is_deleted=False)
        name_field = 'lostie_name'
    if view_type:
        queryset = queryset.filter(view=view_type)
    if color:
        queryset = queryset.filter(color=color)
    if status == 'found':
        views = FoundAnimal.objects.filter(is_deleted=False).values_list('view', flat=True).distinct()
        colors = FoundAnimal.objects.filter(is_deleted=False).values_list('color', flat=True).distinct()
    else:
        views = LostAnimal.objects.filter(is_deleted=False).values_list('view', flat=True).distinct()
        colors = LostAnimal.objects.filter(is_deleted=False).values_list('color', flat=True).distinct()
    paginator = Paginator(queryset.order_by('-id'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'lost_found_list.html', {
        'page_obj': page_obj,
        'views': views,
        'colors': colors,
        'filter': {
            'view': view_type,
            'color': color,
            'status': status,
        }
    })

def found_animal_detail(request, animal_id):
    animal = get_object_or_404(FoundAnimal, id=animal_id)
    finder = animal.finder
    user = request.user if request.user.is_authenticated else None
    messages = Message.objects.filter(found_animal=animal).order_by('created_at')
    can_close = user and user == finder
    if request.method == 'POST' and user:
        if request.POST.get('action') == 'delete' and can_close:
            animal.is_deleted = True
            animal.save()
            return redirect('/lost-found/?status=found')
        text = request.POST.get('text', '').strip()
        if text:
            recipient = finder
            Message.objects.create(sender=user, recipient=recipient, text=text, found_animal=animal)
            return redirect(request.path_info)
    messages = Message.objects.filter(found_animal=animal).order_by('created_at')
    return render(request, 'found_animal_detail.html', {
        'animal': animal,
        'messages': messages,
        'finder': finder,
        'user': user,
        'can_close': can_close,
    })

def lost_animal_detail(request, animal_id):
    animal = get_object_or_404(LostAnimal, id=animal_id)
    user = request.user if request.user.is_authenticated else None
    from .models import Message
    messages = Message.objects.filter(lost_animal=animal).order_by('created_at')
    owner = animal.owner
    chat_participants = set(messages.values_list('sender', flat=True)) - {owner.id}
    if request.method == 'POST' and user:
        action = request.POST.get('action')
        if action == 'delete' and user == owner:
            animal.is_deleted = True
            animal.save()
            return redirect('/lost-found/?status=lost')
        text = request.POST.get('text', '').strip()
        if text:
            if user == owner:
                recipient_id = request.POST.get('recipient_id')
                if recipient_id and int(recipient_id) in chat_participants:
                    recipient = CustomUser.objects.get(id=recipient_id)
                    Message.objects.create(sender=user, recipient=recipient, text=text, lost_animal=animal)
                else:
                    for pid in chat_participants:
                        recipient = CustomUser.objects.get(id=pid)
                        Message.objects.create(sender=user, recipient=recipient, text=text, lost_animal=animal)
            else:
                recipient = owner
                Message.objects.create(sender=user, recipient=recipient, text=text, lost_animal=animal)
            return redirect(request.path_info)
    messages = Message.objects.filter(lost_animal=animal).order_by('created_at')
    return render(request, 'lost_animal_detail.html', {
        'animal': animal,
        'messages': messages,
        'user': user,
        'owner': owner,
        'chat_participants': CustomUser.objects.filter(id__in=chat_participants) if user == owner else None,
    })

@login_required
def chats_list(request):
    user = request.user
    from .models import Message, FoundAnimal, LostAnimal
    if request.method == 'POST' and request.POST.get('action') == 'delete':
        chat_type = request.POST.get('chat_type')
        chat_id = request.POST.get('chat_id')
        if chat_type == 'found':
            try:
                animal = FoundAnimal.objects.get(id=chat_id)
                Message.objects.filter(found_animal=animal).delete()
            except FoundAnimal.DoesNotExist:
                pass
        elif chat_type == 'lost':
            try:
                animal = LostAnimal.objects.get(id=chat_id)
                Message.objects.filter(lost_animal=animal).delete()
            except LostAnimal.DoesNotExist:
                pass
        return redirect(request.path_info)
    user_messages = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).order_by('-created_at')
    chat_dict = {}
    archive_dict = {}
    for msg in user_messages:
        key = None
        obj = None
        is_archive = False
        if msg.found_animal:
            key = f'found_{msg.found_animal.id}'
            obj = msg.found_animal
            is_archive = msg.found_animal.is_matched or msg.found_animal.is_deleted
        elif msg.lost_animal:
            key = f'lost_{msg.lost_animal.id}'
            obj = msg.lost_animal
            is_archive = (msg.lost_animal.is_found or msg.lost_animal.is_deleted)
        if key and obj:
            d = archive_dict if is_archive else chat_dict
            if key not in d:
                d[key] = {'obj': obj, 'last_msg': msg, 'type': 'found' if msg.found_animal else 'lost'}
    chats = sorted(chat_dict.values(), key=lambda x: x['last_msg'].created_at, reverse=True)
    archive_chats = sorted(archive_dict.values(), key=lambda x: x['last_msg'].created_at, reverse=True)
    return render(request, 'chats_list.html', {'chats': chats, 'archive_chats': archive_chats})

# Create your views here.
