# config.py — єдине місце, де застосунок торкається середовища.
import os

class MissingConfig(Exception):
    pass

def require(name: str) -> str:
    """Обов'язкове значення: немає — падаємо ЗАРАЗ, а не колись потім."""
    value = os.environ.get(name)
    if not value:
        raise MissingConfig(f"немає обов'язкової змінної середовища {name}")
    return value

def optional(name: str, default: str) -> str:
    return os.environ.get(name) or default

class Config:
    DATABASE_URL = require("DATABASE_URL")
    SECRET_KEY   = require("SECRET_KEY")
    PORT         = int(optional("PORT", "8000"))
    LOG_LEVEL    = optional("LOG_LEVEL", "info")

# Читаємо ОДИН раз при імпорті — тобто на старті процесу.
# Забули задати SECRET_KEY у проді? Процес не підніметься взагалі,
# і ти дізнаєшся про це на деплої, а не з нічної пейджер-тривоги.
config = Config()
