import asyncio

def dump_active_tasks():
    loop = asyncio.get_running_loop()
    tasks = asyncio.all_tasks(loop)
    print(f"[*] Активних задач у циклі: {len(tasks)}")
    for t in tasks:
        print(f"--- Задача: {t.get_name()} ---")
        # Друк поточного стека виконання корутини
        t.print_stack()
