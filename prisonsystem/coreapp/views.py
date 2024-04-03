from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import UserRegisterForm


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
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'coreapp/user/login.html')
def user_profile(request):
    return render(request, 'coreapp/user/profile.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('home')) 
    else:
        form = UserRegisterForm()
    return render(request, 'coreapp/user/register.html', {'form': form})
