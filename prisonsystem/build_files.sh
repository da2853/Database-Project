pip install -r requirements.txt

echo "Collect Static..."
python3.9 manage.py collectstatic --noinput --clear