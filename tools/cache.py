from fsspec import json
import redis
import sys
import json
import hashlib

CACHE_TTL=30

def connectRedis():
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            socket_timeout=5
        )
        ping = client.ping()
        if ping is True: 
            print("Connection Established!")
            return client
    except redis.AuthenticationError:
        print("Authentication Error")
        sys.exit(1)
    except redis.ConnectionError:
        print("Redis connection failed")
        sys.exit(1)

client = connectRedis()

def setDataToCache(cache_key,analysis):
    client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(analysis)
    )

def getDataFromCache(cache_key):
    data = client.get(cache_key)
    if data is None:
        return None
    return json.loads(data)

def deleteFromCache(cache_key):
    client.delete(cache_key)

def createCacheKey(query: str):
    return hashlib.sha256(query.lower().strip().encode()).hexdigest()