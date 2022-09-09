# build_files.sh
pip install -r requirements.txt
python3.9.5 manage.py makemigrations
python3.9.5 manage.py migrate
