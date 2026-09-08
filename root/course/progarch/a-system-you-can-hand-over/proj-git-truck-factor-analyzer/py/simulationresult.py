from dataclasses import dataclass, field


@dataclass
class SimulationResult:
    # Результат моделювання автобусного фактора системи
    truck_factor: int
    critical_developers: list[str]
    orphan_progression: list[float]
    total_files: int
    unowned_initially: int


def calculate_truck_factor(
    file_owners: dict[str, set[str]],
    collapse_threshold: float = 0.5,
) -> SimulationResult:
    # Обчислює автобусний фактор репозиторію методом жадібного вилучення
    total_files = len(file_owners)
    if total_files == 0:
        return SimulationResult(0, [], [0.0], 0, 0)

    # Виявлення файлів, які не мають жодного первинного власника від самого початку
    initially_orphan = {f for f, owners in file_owners.items() if not owners}
    orphan_files = set(initially_orphan)

    # Збір множини всіх діючих інженерів
    active_devs: set[str] = set()
    for owners in file_owners.values():
        active_devs.update(owners)

    departed_devs: list[str] = []
    progression: list[float] = [len(orphan_files) / total_files]

    # Якщо початкова частка сирітського коду вже перевищує поріг
    if progression[0] >= collapse_threshold:
        return SimulationResult(0, [], progression, total_files, len(initially_orphan))

    while active_devs:
        # Шукаємо розробника, чий вихід створить найбільше нових сирітських файлів
        best_dev = None
        max_new_orphans = -1
        best_new_orphan_set: set[str] = set()

        for dev in active_devs:
            # Файли, де dev є єдиним власником серед тих, хто ще залишився
            new_orphans = {
                f
                for f in file_owners
                if f not in orphan_files
                and file_owners[f] & active_devs == {dev}
            }
            if len(new_orphans) > max_new_orphans:
                max_new_orphans = len(new_orphans)
                best_dev = dev
                best_new_orphan_set = new_orphans

        if best_dev is None or max_new_orphans == 0:
            # Решта розробників не мають унікальних файлів: подальший вихід
            # не збільшує сирітство, доки не вийдуть їхні спільні колеги
            # Беремо розробника з найбільшою загальною кількістю перекриттів
            best_dev = max(
                active_devs,
                key=lambda d: sum(1 for f in file_owners if d in file_owners[f]),
            )
            best_new_orphan_set = set()

        active_devs.remove(best_dev)
        departed_devs.append(best_dev)
        orphan_files.update(best_new_orphan_set)

        current_loss = len(orphan_files) / total_files
        progression.append(current_loss)

        # Перевірка умови досягнення критичного колапсу
        if current_loss >= collapse_threshold:
            break

    return SimulationResult(
        truck_factor=len(departed_devs),
        critical_developers=departed_devs,
        orphan_progression=progression,
        total_files=total_files,
        unowned_initially=len(initially_orphan),
    )
