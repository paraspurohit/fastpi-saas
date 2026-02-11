from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    rate_limit: int = 200
    rate_window: int = 60
    cache_ttl: int = 10
    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        # TODO check which env file to use .env for local and .env.prod for production
        env_file = '.env'

setting = Settings()
