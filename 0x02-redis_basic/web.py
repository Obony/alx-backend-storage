import requests
import redis
from functools import wraps

# Initialize a Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def cache_request_result(url):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use the URL as the cache key
            cache_key = f"cache:{url}"
            cached_result = redis_client.get(cache_key)

            if cached_result:
                return cached_result.decode('utf-8')

            result = func(*args, **kwargs)
            # Cache the result with a 10-second expiration time
            redis_client.setex(cache_key, 10, result)
            return result

        return wrapper

    return decorator

@cache_request_result
def get_page(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

# Example usage
if __name__ == "__main__":
    slow_url = "http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.example.com"
    
    # Access the slow URL twice to see caching in action
    for _ in range(2):
        page = get_page(slow_url)
        if page:
            print(page)
        else:
            print("Failed to retrieve the page.")

