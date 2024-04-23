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
def activity(request):
    return render(request, 'coreapp/activity.html')

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
                cursor.execute(f"SELECT retrieve_user_id_from_session(%s)", [request.user.id])
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

from django.http import JsonResponse
import json
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def edit_record(request):
    print("start")
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        print("load faileds")
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

    table = data.get('table')
    record_id = data.get('record_id')
    search_value = data.get('search_value')

    # Define a mapping from table names to their primary key fields
    table_to_id_field = {
        'criminals': 'Criminal_ID',
        'crimes': 'Crime_ID',
        'charges': 'Crime_ID',
        'sentencing': 'Crime_ID',
        'criminal_phone': 'Criminal_ID',
        'aliases': 'Criminal_ID',
        'address': 'Criminal_ID',
        'hearing': 'Crime_ID',
        'monetary': 'Crime_ID',
        'appeals': 'Crime_ID',
        'arresting_officers': 'Crime_ID',
        'officer': 'Badge_Number',
        'officer_phone': 'Badge_Number',
        'users': 'user_id',
        'user_activity': 'activity_id'
    }

    record_id_field = table_to_id_field.get(table)
    print('checking')
    if not record_id_field:
        return JsonResponse({'success': False, 'error': 'Invalid table specified.'}, status=400)

    fields = {key: value for key, value in data.items() if key not in ['csrfmiddlewaretoken', 'table', 'record_id']}
    fields[record_id_field] = record_id

    set_values = ', '.join([f"{key} = %({key})s" for key in fields.keys() if key != record_id_field])
    print("fields: ", fields)
    try:
        with connection.cursor() as cursor:
            if table == 'charges':
                cursor.execute(f"UPDATE charges SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'arresting_officers':
                query = f"SELECT * FROM arresting_officers WHERE Crime_ID = %s AND Badge_ID = %s"
                cursor.execute(query, (int(search_value), int(search_value)))
            elif table == 'criminals':
                cursor.execute(f"UPDATE criminals SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'crimes':
                cursor.execute(f"UPDATE crimes SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'sentencing':
                cursor.execute(f"UPDATE sentencing SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'criminal_phone':
                cursor.execute(f"UPDATE criminal_phone SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'aliases':
                cursor.execute(f"UPDATE aliases SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'address':
                cursor.execute(f"UPDATE address SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'hearing':
                cursor.execute(f"UPDATE hearing SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'monetary':
                cursor.execute(f"UPDATE monetary SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'appeals':
                cursor.execute(f"UPDATE appeals SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'officer':
                cursor.execute(f"UPDATE officer SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'officer_phone':
                cursor.execute(f"UPDATE officer_phone SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'users':
                cursor.execute(f"UPDATE users SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            elif table == 'user_activity':
                cursor.execute(f"UPDATE user_activity SET {set_values} WHERE {record_id_field} = %({record_id_field})s", fields)
            else:
                raise ValueError(f"Invalid table name: {table}")
            return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required
def delete_record(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)
    data = json.loads(request.body)
    table = data.get('table')
    record = data.get('record')

    try:
        with connection.cursor() as cursor:
            if table == 'criminals':
                criminal_id = record['criminal_id']
                delete_queries = [
                    "DELETE FROM criminal_phone WHERE Criminal_ID = %s",
                    "DELETE FROM aliases WHERE Criminal_ID = %s",
                    "DELETE FROM address WHERE Criminal_ID = %s",
                    "DELETE FROM crimes WHERE Criminal_ID = %s",
                    "DELETE FROM criminals WHERE Criminal_ID = %s"
                ]
                for query in delete_queries:
                    cursor.execute(query, [criminal_id])
                
            elif table == 'crimes':
                crime_id = record['crime_id']
                delete_queries = [
                    "DELETE FROM charges WHERE Crime_ID = %s",
                    "DELETE FROM sentencing WHERE Crime_ID = %s",
                    "DELETE FROM hearing WHERE Crime_ID = %s",
                    "DELETE FROM monetary WHERE Crime_ID = %s",
                    "DELETE FROM appeals WHERE Crime_ID = %s",
                    "DELETE FROM arresting_officers WHERE Crime_ID = %s",
                    "DELETE FROM crimes WHERE Crime_ID = %s"
                ]
                for query in delete_queries:
                    cursor.execute(query, [crime_id])

            elif table == 'officer':
                badge_number = record['badge_number']
                delete_queries = [
                    "DELETE FROM officer_phone WHERE Badge_Number = %s",
                    "DELETE FROM arresting_officers WHERE Badge_ID = %s",
                    "DELETE FROM officer WHERE Badge_Number = %s"
                ]
                for query in delete_queries:
                    cursor.execute(query, [badge_number])

            elif table == 'sentencing':
                crime_id = record['crime_id']
                query = "DELETE FROM sentencing WHERE crime_id = %s"
                cursor.execute(query, [crime_id])

            elif table == 'criminal_phone':
                number = record['number']
                query = "DELETE FROM criminal_phone WHERE number = %s"
                cursor.execute(query, [number])
            
            elif table == 'aliases':
                alias = record['alias']
                query = "DELETE FROM aliases WHERE alias = %s"
                cursor.execute(query, [alias])

            elif table == 'address':
                addr = record['addr']
                query = "DELETE FROM address WHERE addr = %s"
                cursor.execute(query, [addr])

            elif table == 'hearing':
                crime_id = record['crime_id']
                query = "DELETE FROM hearing WHERE crime_id = %s"
                cursor.execute(query, [crime_id])
            
            elif table == 'monetary':
                crime_id = record['crime_id']
                query = "DELETE FROM monetary WHERE crime_id = %s"
                cursor.execute(query, [crime_id])
            
            elif table == 'appeals':
                crime_id = record['crime_id']
                query = "DELETE FROM appeals WHERE crime_id = %s"
                cursor.execute(query, [crime_id])

            elif table == 'officer_phone':
                number = record['number']
                query = "DELETE FROM officer_phone WHERE number = %s"
                cursor.execute(query, [number])

            else:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
