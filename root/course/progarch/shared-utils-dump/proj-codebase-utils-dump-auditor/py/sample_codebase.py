"""
sample_codebase.py
Демонстраційна кодова база з аномаліями у спільному пакеті утиліт.
Надає синтетичні файли для тестування аналізатора утиліт без зовнішніх залежностей.
"""

from pathlib import Path
from typing import Dict, List, Tuple


SAMPLE_UTILS_CODE = '''# utils/helpers.py
from typing import Optional

class Order:
    """Доменний клас замовлення."""
    pass

class User:
    """Доменний клас користувача."""
    pass

def unused_formatter(text: str) -> str:
    """Аномалія 1: Мертвий код (DEAD_CODE, Ca = 0) - ніде не викликається."""
    return text.strip().upper()

def format_single_user_header(name: str, email: str) -> str:
    """Аномалія 2: Локальний хелпер (LOCAL_HELPER, Ca = 1) - використовується тільки в user_service."""
    return f"User: {name} <{email}>"

def calculate_discount(order: Order, val: float) -> float:
    """Аномалія 3: Витік бізнес-логіки (DOMAIN_LEAK) - доменна сутність Order у сигнатурі."""
    return val * 0.9

def sanitize_string(input_str: str) -> str:
    """Легітимна спільна бібліотека (SHARED_LIBRARY, Ca = 2) - використовується в двох сервісах."""
    return input_str.strip().lower()
'''

SAMPLE_USER_SERVICE_CODE = '''# services/user_service.py
from utils.helpers import format_single_user_header, sanitize_string

def process_user_data(name: str, email: str) -> str:
    clean_name = sanitize_string(name)
    return format_single_user_header(clean_name, email)
'''

SAMPLE_ORDER_SERVICE_CODE = '''# services/order_service.py
from utils.helpers import calculate_discount, sanitize_string

def process_order_total(raw_price: str) -> float:
    cleaned = sanitize_string(raw_price)
    price = float(cleaned)
    return calculate_discount(None, price)
'''


def get_sample_sources() -> Tuple[Dict[str, str], Dict[str, str], List[str]]:
    """
    Повертає словники джерел коду утиліт, джерел коду клієнтів та перелік доменних типів.
    """
    utils_sources = {
        "utils/helpers.py": SAMPLE_UTILS_CODE,
    }
    client_sources = {
        "services/user_service.py": SAMPLE_USER_SERVICE_CODE,
        "services/order_service.py": SAMPLE_ORDER_SERVICE_CODE,
    }
    domain_types = ["Order", "User", "Payment", "Invoice"]

    return utils_sources, client_sources, domain_types


def create_sample_files(base_dir: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Створює фізичні файли демонстраційної кодової бази у вказаному каталозі.
    Повертає (шляхи_до_утиліт, шляхи_до_клієнтів, список_доменних_типів).
    """
    base_path = Path(base_dir)
    utils_sources, client_sources, domain_types = get_sample_sources()

    utils_files = []
    for rel_path, code in utils_sources.items():
        file_path = base_path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code, encoding="utf-8")
        utils_files.append(str(file_path))

    client_files = []
    for rel_path, code in client_sources.items():
        file_path = base_path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code, encoding="utf-8")
        client_files.append(str(file_path))

    return utils_files, client_files, domain_types
