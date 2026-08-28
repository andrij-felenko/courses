import sys
from pathlib import Path
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename


def inspect_wheel_compatibility(wheel_path_str: str) -> None:
    """Перевірити сумісність wheel-файлу з поточним середовищем Python."""
    wheel_path = Path(wheel_path_str)
    
    # 1. Розбір назви колеса на компоненти (PEP 425)
    name, version, build, tags = parse_wheel_filename(wheel_path.name)
    
    print(f"Пакет: {name} (версія {version})")
    print(f"Теги колеса: {[str(t) for t in tags]}")
    
    # 2. Отримання списку сумісних системних тегів
    current_system_tags = list(sys_tags())
    print(f"Системне середовище: {current_system_tags[0]}")
    
    # 3. Перевірка перетину множин тегів
    matching_tags = [t for t in tags if t in current_system_tags]
    
    if matching_tags:
        best_match = matching_tags[0]
        priority_index = current_system_tags.index(best_match)
        print(f"Статус: СУМІСНИЙ")
        print(f"Найкращий збіг: {best_match} (індекс пріоритету: {priority_index})")
    else:
        print("Статус: НЕСУМІСНИЙ")
        print("Причина: жоден із тегів колеса не знайдено серед підтримуваних тегів середовища.")
        print("pip спробує завантажити sdist або іншу версію wheel.")


if __name__ == "__main__":
    example_wheel = f"cryptography-42.0.5-cp39-abi3-manylinux_2_28_x86_64.whl"
    inspect_wheel_compatibility(example_wheel)
