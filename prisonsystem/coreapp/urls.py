from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/inmate/', views.add_inmate, name='add_inmate'),
    path('add/officer/', views.add_officer, name='add_officer'),
    path('add/sentence/', views.add_sentence, name='add_sentence'),
    path('details/crime/', views.crime_details, name='crime_details'),
    path('details/inmate/', views.inmate_details, name='inmate_details'),
    path('details/officer/', views.officer_details, name='officer_details'),
    path('results/inmate/', views.inmate_results, name='inmate_results'),
    path('results/officer/', views.officer_results, name='officer_results'),
    path('search/inmate/', views.inmate_search, name='inmate_search'),
    path('search/officer/', views.officer_search, name='officer_search'),
    path('login/', views.user_login, name='user_login'),
    path('profile/', views.user_profile, name='user_profile'),
    path('register/', views.user_register, name='user_register'),
    path('query/', views.query, name='query'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('execute-query/', views.execute_query, name='execute_query'),
]