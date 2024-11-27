from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.cache import cache
from urlgen.tasks import increment_counter, get_counter_value
from django.http import HttpResponseNotFound, HttpResponse

class FetchShortURL(APIView):
    def get(self, request, surl):
        lock_key = f"lock:{surl}" #defining a lock key
        lock_timeout = 1
        try:
            cached_res = cache.get(surl) #the entry must be present in cache 
            if cache.get(lock_key): #locked to avoid race conditions (would not work in a distributed environment)
                if cached_res:
                    return HttpResponseRedirect(cached_res)
                else:
                    return HttpResponseNotFound("The page you're looking for does not exist.")
            else:
                cache.set(lock_key, True, timeout=lock_timeout) #setting a lock so that the counter can be incremented accurately
                if cached_res:
                    increment_counter.delay(surl)
                    return HttpResponseRedirect(cached_res)
                else:
                    return HttpResponseNotFound("The page you're looking for does not exist.")
        except:
            return Response({'success':False,'message':'Internal Server Error'}, status=status.HTTP_400_BAD_REQUEST)

class FetchUrlCounter(APIView):
    def get(self, request, surl):
        try:
            counter_val = get_counter_value(surl)
            if counter_val=="Not found":
                return HttpResponseNotFound("The page you're looking for does not exist.")
            return HttpResponse(f"The url {surl} has been accessed {counter_val} times")
        except Exception as e:
            return HttpResponseNotFound("The page you're looking for does not exist.")