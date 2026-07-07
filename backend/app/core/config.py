from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "EAMS"
    ENV: str = "dev"
    SECRET_KEY: str = "change-me-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7
    DATABASE_URL: str = "postgresql://eams:eams@localhost:5432/eams"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost"
    # business rules
    WORK_START: str = "09:00"          # official day start
    WORK_END: str = "18:00"            # official day end
    LATE_GRACE_MINUTES: int = 10       # grace before marked late
    FULL_DAY_HOURS: float = 8.0        # hours needed for a full day
    HALF_DAY_HOURS: float = 4.0
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
