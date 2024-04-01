from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from prisonsystem.forms import UserRegisterForm


def home(request):
    return render(request, 'coreapp/home.html')

def add_inmate(request):
    return render(request, 'coreapp/add/add_inmate.html')

def add_officer(request):
    return render(request, 'coreapp/add/add_officer.html')

def add_sentence(request):
    return render(request, 'coreapp/add/add_sentence.html')

def crime_details(request):
    return render(request, 'coreapp/details/crime_details.html')

def inmate_details(request):
    return render(request, 'coreapp/details/inmate_details.html')

def officer_details(request):
    return render(request, 'coreapp/details/officer_details.html')

def inmate_results(request):
    return render(request, 'coreapp/results/inmate_results.html')

def officer_results(request):
    return render(request, 'coreapp/results/officer.results.html')

def inmate_search(request):
    return render(request, 'coreapp/search/inmate_search.html')

def officer_search(request):
    return render(request, 'coreapp/search/officer_search.html')

def user_login(request):
    return render(request, 'coreapp/user/login.html')

def user_profile(request):
    return render(request, 'coreapp/user/profile.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('')) 
        form = UserRegisterForm()
    return render(request, 'coreapp/user/register.html', {'form': form})

