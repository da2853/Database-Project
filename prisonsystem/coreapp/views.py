from django.contrib.auth import authenticate, login
from django.db import transaction, IntegrityError
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
        email = request.POST.get('username')
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
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            
            try:
                with transaction.atomic():
                    if User.objects.filter(username=username).exists():
                        form.add_error('email', 'Username already exists. Please choose a different one.')
                    else:
                        # Save the user
                        user = form.save()
                        role = 'read_only'

                        # Create and grant roles in the database using raw SQL
                        with connection.cursor() as cursor:
                            cursor.execute('CREATE USER "%s" WITH PASSWORD \'%s\'' % (username, password))
                            cursor.execute('GRANT %s TO "%s"' % (role, username))
                        # Log in the user and redirect to another page
                        login(request, user)
                        return redirect(reverse('query'))

            except IntegrityError:
                form.add_error('email', 'This username is already taken. Please try again.')

    else:
        form = UserRegisterForm()

    return render(request, 'coreapp/user/register.html', {'form': form})
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
def execute_query(request):
    if request.method == 'POST':
        sql_query = request.POST.get('query')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET ROLE %s", [request.user.username])
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

@csrf_exempt
@login_required
def execute_raw_sql(request):
    if request.method == 'POST':
        sql_command = request.POST.get('sql_command')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET ROLE %s", [request.user.username])
                cursor.execute(sql_command)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)