from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.cache import cache
import multiprocessing
from .env_vars import predef_string, max_retries
import hashlib
from django.core.validators import URLValidator
from .models import URLdb
from django.db.models import Q
from django.http import HttpResponseRedirect
from urllib.parse import urlparse
from .tasks import save_to_db

def hash_short_url(url):
    try:
        result = hashlib.sha3_256(url.encode()).hexdigest()
        if len(result) > 7:
            return result[:7]
        else:
            return result
    except Exception as e:
        return None

def generate_short_url(url, max_retries):
    cnt = max_retries
    while(max_retries):
        shortened_url = hash_short_url(url)
        if cache.get(shortened_url):
            cnt = cnt - 1
            url += predef_string
            continue
        else:
            save_to_db.delay(shortened_url)
            #two way caching for faster processing
            cache.set(shortened_url,url,timeout=604800) #setting the TTL to 7 days
            cache.set(url,shortened_url,timeout=604800) #setting the TTL to 7 days
            break
    return shortened_url

class GenerateShortURL(APIView):
    def post(self, request):
        current_url = request.build_absolute_uri() #needs to be changed to a constant when deployed
        parsed_url = urlparse(current_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        try:
            url = request.data['url']
            validator = URLValidator()
            validator(url)
        except:
            return Response({'success':False,'message':'Please input a valid url'},status=status.HTTP_400_BAD_REQUEST)
        if cache.get(url):
            short_url_cached = f"{base_url}/{cache.get(url)}"
            return Response({'success':True,'short url':short_url_cached},status=status.HTTP_200_OK)
        pool = multiprocessing.Pool(processes=4)
        result = pool.apply_async(generate_short_url, args=(url, max_retries))
        pool.close()
        pool.join()
        shortened_url = result.get()
        short_url = f"{base_url}/{shortened_url}"
        if result.get():
            return Response({'success':True,'short url':short_url},status=status.HTTP_200_OK)
        else:
            return Response({'success':False,'message':'Internal Server Error'},status=status.HTTP_400_BAD_REQUEST)



