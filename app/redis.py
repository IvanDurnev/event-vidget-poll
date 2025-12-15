import redis
from app import Config

redis_client = redis.Redis.from_url(
    Config.REDIS_URL,
    decode_responses=True
)