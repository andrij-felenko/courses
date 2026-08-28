from dataclasses import dataclass

# Логічний контейнер зі статичної моделі — те, що на статиці одна «коробка».
@dataclass(frozen=True)
class Container:
    name: str   # "api" або "db" — назва з логічної моделі

# Вузол розгортання — місце, де крутяться копії (сервер / VM / контейнер).
@dataclass(frozen=True)
class Deployment:
    node: str            # напр. "eu-node-1"
    of: Container        # ЯКИЙ логічний контейнер тут живе
    replicas: int        # СКІЛЬКИ копій — ось чого немає на статиці

# Скільки всього копій цього контейнера піднято в цьому середовищі.
def total_replicas(deps: list[Deployment], name: str) -> int:
    # той самий логічний контейнер → сумуємо копії по всіх вузлах
    return sum(d.replicas for d in deps if d.of.name == name)
