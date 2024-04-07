from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import UserRegisterForm
from django.db import connection


def home(request):
    if request.user.is_authenticated:
        return query(request)
    else:
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

def user_profile(request):
    return render(request, 'coreapp/user/profile.html')

@csrf_protect
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('query')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'coreapp/user/login.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already exists. Please choose a different one.')
            else:
                user = form.save()
                
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO users (first_name, last_name, username, email) VALUES (%s, %s, %s, %s)",
                                   [user.first_name, user.last_name, user.username, user.email])
                
                login(request, user)
                return redirect(reverse('query'))
    else:
        form = UserRegisterForm()

    return render(request, 'coreapp/user/register.html', {'form': form})

@csrf_exempt
@login_required
def query(request):
    if request.method == 'POST':
        sql_query = request.POST.get('query')
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                # Assuming you don't want to return actual data for security reasons
                return JsonResponse({'success': 'Query executed successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'coreapp/query.html')


@csrf_exempt
@login_required
def query_limited(request):
    if request.method == 'POST':
        sql_query = request.POST.get('query').strip()

        if not sql_query.lower().startswith('select'):
            return JsonResponse({'error': 'Only SELECT queries are allowed.'}, status=403)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]

                return JsonResponse({'success': 'Query executed successfully.', 'results': results})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'coreapp/query.html')


@csrf_exempt
@login_required
def execute_query(request):
    if request.method == 'POST':
        sql_query = request.POST.get('query')

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)

                if sql_query.lower().startswith('select'):
                    rows = cursor.fetchall()
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return JsonResponse({'success': True, 'results': results})
                else:
                    return JsonResponse({'success': True, 'message': 'Query executed successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def log_user_activity(user_id, activity_description):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO user_activity (user_id, activity_description) VALUES (%s, %s)",
                       [user_id, activity_description])