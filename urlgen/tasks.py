from .models import URLdb
from urlshort.celery import app
from django.utils import timezone
from django.db.models import F

@app.task(bind=True)
def save_to_db(self, shortened_url):
    try:
        url_db_obj = URLdb()
        url_db_obj.short_url_key = shortened_url
        url_db_obj.save()
        return True
    except Exception as e:
        self.retry(countdown=2, exc=e, max_retries=2)
        return False

@app.task(bind=True)
def increment_counter(self, shortened_url):
    try:
        URLdb.objects.filter(short_url_key=shortened_url).update(hits=F('hits') + 1)
        return True
    except Exception as e:
        self.retry(countdown=2, exc=e, max_retries=2)
        return False

@app.task(bind=True)
def delete_expired_urls(self):
    try:
        expired_urls = URLdb.objects.filter(expires_at__lt=timezone.now())
        expired_urls_count = expired_urls.count()
        expired_urls.delete()
        return f"Deleted {expired_urls_count} expired URLs."
    except Exception as e:
        self.retry(countdown=2, exc=e, max_retries=2)
        return False

def get_counter_value(short_url):
    try:
        url_obj_hits = URLdb.objects.get(short_url_key=short_url).hits
        return url_obj_hits
    except Exception as e:
        return "Not found"