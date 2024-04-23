import json
from django.contrib.auth import authenticate, login, logout
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

@csrf_protect
@login_required
def search_view(request):
    return render(request, 'coreapp/search.html')

@csrf_protect
@login_required
def create_view(request):
    return render(request, 'coreapp/create.html')

def user_profile(request):
    return render(request, 'coreapp/user/profile.html')

@csrf_protect
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
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
                        form.add_error('email', 'Email already in use. Please choose a different one.')
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
                # cursor.execute("SET ROLE %s", [request.user.username])
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


def logout_view(request):
    logout(request)
    return redirect('home')

@csrf_protect
@login_required
def create_view(request):
    if request.method == 'POST':
        table = request.POST.get('table')
        fields = request.POST.dict()
        fields.pop('csrfmiddlewaretoken', None)
        fields.pop('table', None)

        placeholders = ', '.join(['%s'] * len(fields))
        columns = ', '.join(fields.keys())
        values = tuple(fields.values())

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            messages.success(request, 'Record created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating record: {str(e)}')

    return render(request, 'coreapp/create.html')

@csrf_exempt
@login_required
def perform_search(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)
    data = json.loads(request.body)
    table = data.get('table')
    search_value = data.get('search_value', '')

    query_dict = {
        'criminals': "SELECT * FROM criminals WHERE criminal_id = %s OR name ILIKE %s",
        'crimes': "SELECT * FROM crimes WHERE Crime_ID = %s OR Crime_Code ILIKE %s OR Classification ILIKE %s",
        'charges': "SELECT * FROM charges WHERE Crime_ID = %s OR Charge_Status ILIKE %s",
        'sentencing': "SELECT * FROM sentencing WHERE Crime_ID = %s OR Sentence_Type ILIKE %s",
        'criminal_phone': "SELECT * FROM criminal_phone WHERE Criminal_ID = %s OR Number ILIKE %s",
        'aliases': "SELECT * FROM aliases WHERE Criminal_ID = %s OR Alias ILIKE %s",
        'address': "SELECT * FROM address WHERE Criminal_ID = %s OR Addr ILIKE %s OR City ILIKE %s OR State ILIKE %s OR Zip_Code ILIKE %s",
        'hearing': "SELECT * FROM hearing WHERE Crime_ID = %s OR Hearing_Date::text ILIKE %s OR Appeal_Cutoff_Date::text ILIKE %s",
        'monetary': "SELECT * FROM monetary WHERE Crime_ID = %s",
        'appeals': "SELECT * FROM appeals WHERE Crime_ID = %s OR Appeal_Status ILIKE %s",
        'arresting_officers': "SELECT * FROM arresting_officers WHERE Crime_ID = %s OR Badge_ID = %s",
        'officer': "SELECT * FROM officer WHERE Badge_Number = %s OR Name ILIKE %s OR Precinct ILIKE %s OR Officer_Status ILIKE %s",
        'officer_phone': "SELECT * FROM officer_phone WHERE Badge_Number = %s OR Number ILIKE %s"
    }

    try:
        query = query_dict.get(table)
        if not query:
            return JsonResponse({'success': False, 'error': 'Invalid table selected.'}, status=400)
        if search_value == '':
            complete_query = "SELECT * FROM " + table
        else:
            params = [search_value] + ['%' + search_value + '%'] * (query.count('%s') - 1)
            if table in ['criminals', 'criminal_phone', 'aliases', 'address', 'arresting_officers', 'charges', 'crimes', 'sentencing', 'officer', 'appeals', 'hearing', 'monetary', 'officer_phone']:
                try:
                    params[0] = int(search_value) if search_value.isdigit() else None
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Expected a numerical value.'}, status=400)
            
            complete_query = query

        with connection.cursor() as cursor:
            if search_value == '':
                cursor.execute(complete_query)
            else:
                cursor.execute(complete_query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

        return JsonResponse({'success': True, 'results': results})

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred: ' + str(e)}, status=400)


@csrf_exempt
@login_required
def edit_record(request):
    if request.method == 'POST':
        table = request.POST.get('table')
        record_id = request.POST.get('record_id')
        fields = request.POST.dict()
        fields.pop('csrfmiddlewaretoken', None)
        fields.pop('table', None)
        fields.pop('record_id', None)

        set_values = ', '.join([f"{key} = %s" for key in fields.keys()])
        values = tuple(fields.values()) + (record_id,)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"UPDATE {table} SET {set_values} WHERE {'Criminal_ID' if table == 'criminals' else 'Crime_ID'} = %s", values)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


@csrf_exempt
@login_required
def delete_record(request):
    if request.method == 'POST':
        table = request.POST.get('table')
        record_id = request.POST.get('record_id')

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table} WHERE {'Criminal_ID' if table == 'criminals' else 'Crime_ID'} = %s", [record_id])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)