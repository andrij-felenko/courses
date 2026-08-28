import multiprocessing
import sys

def worker_task(task_id: int):
    print(f"Обробка задачі {task_id} у дочірньому процесі")

if __name__ == "__main__":
    # КРИТИЧНО для заморожених застосунків на Windows/macOS:
    multiprocessing.freeze_support()

    # Подальша безпечна робота з пулом процесів:
    processes = [multiprocessing.Process(target=worker_task, args=(i,)) for i in range(4)]
    for p in processes: p.start()
    for p in processes: p.join()
