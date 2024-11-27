Steps to run the application:

Install dependencies using pip3 install -r req.txt


Install redis using the link https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/

Run the commands:


python3 manage.py makemigrations

python3 manage.py migrate


Run this command and set username, pass as per your wish:

python3 manage.py createsuperuser


Finally run the django server:

python3 manage.py runserver


Also run these two commands in separate terminals:

celery -A urlshort worker --concurrency=3 -l info

celery -A urlshort beat --loglevel=info


The detailed documentation is present here:

https://docs.google.com/document/d/1L3iXwlcwcLLz1d8VFA1U9whqbHKQZWW7XKofVmDcCKE/edit?usp=sharing
