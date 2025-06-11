# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('add-lost/', views.add_lost, name='add_lost'),
    path('add-found/', views.add_found, name='add_found'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-shelter/', views.edit_shelter, name='edit_shelter'),
    path('add-animal/', views.add_animal, name='add_animal'),
    path('animal/<int:animal_id>/', views.animal_detail, name='animal_detail'),
    path('take/', views.take_animals, name='take_animals'),
    path('edit-animal/<int:animal_id>/', views.edit_animal, name='edit_animal'),
    path('delete-animal/<int:animal_id>/', views.delete_animal, name='delete_animal'),
    path('lost-found/', views.lost_found_list, name='lost_found_list'),
    path('found-animal/<int:animal_id>/', views.found_animal_detail, name='found_animal_detail'),
    path('lost-animal/<int:animal_id>/', views.lost_animal_detail, name='lost_animal_detail'),
    path('chats/', views.chats_list, name='chats_list'),
    path('get_yandex_coords/', views.get_yandex_coords, name='get_yandex_coords'),
]