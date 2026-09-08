"""
Розрахунок інтервалів повторних спроб з експоненційним бекофом і Full Jitter.
"""

import random
import time


def compute_full_jitter(attempt: int, base_delay: float = 0.1, max_delay: float = 2.0) -> float:
    """
    Обчислює затримку повторної спроби за алгоритмом Full Jitter.

    Формула:
      Cap = min(max_delay, base_delay * 2 ** (attempt - 1))
      Sleep = uniform(0, Cap)

    Чому Full Jitter:
    При масових збоях стороннього API синхронні фіксовані або суто експоненційні
    повтори призводять до резонансних сплесків навантаження (Thundering Herd),
    коли тисячі клієнтів б'ють по відроджуваному серверу в один і той самий міг.
    Full Jitter рівномірно розмиває інтервал повторів по всій часовій осі,
    мінімізуючи взаємну кореляцію запитів і максимізуючи пропускну здатність.
    """
    if attempt <= 0:
        return 0.0

    exp_cap = base_delay * (2 ** (attempt - 1))
    cap = min(max_delay, exp_cap)
    return random.uniform(0.0, cap)


def calculate_next_retry_at(attempt: int, base_delay: float = 0.1, max_delay: float = 2.0) -> float:
    """Повертає абсолютний Unix timestamp наступної спроби."""
    delay = compute_full_jitter(attempt, base_delay, max_delay)
    return time.time() + delay
