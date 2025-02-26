import redis
from datetime import timedelta

#Configure Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

CACHE_TTL = timedelta(hours=1)  # cache time-to-live in seconds