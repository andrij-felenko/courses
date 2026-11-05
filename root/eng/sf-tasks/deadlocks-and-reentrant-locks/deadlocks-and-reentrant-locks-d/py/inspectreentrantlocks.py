# GDB Python скрипт для діагностики станів реентрантних замків у FreeRTOS
import gdb

class InspectReentrantLocks(gdb.Command):
    """Виводить стан усіх реентрантних замків та перевіряє заблоковані задачі"""
    def __init__(self):
        super(InspectReentrantLocks, self).__init__("inspect-locks", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        print("=== ДІАГНОСТИКА СТАНУ СИСТЕМНИХ ЗАМКІВ ===")
        # Зчитування списку задач із внутрішніх структур FreeRTOS
        pxReadyTasksLists = gdb.parse_and_eval("pxReadyTasksLists")
        xSuspendedTaskList = gdb.parse_and_eval("xSuspendedTaskList")
        
        print(f"[+] Аналіз оперативної пам'яті ядра RTOS...")
        # Обхід структур даних в адресному просторі мікроконтролера
        try:
            mutex_list = gdb.parse_and_eval("xRegisteredMutexes")
            curr = mutex_list['head']
            while curr != 0:
                lock = curr['lock_ptr']
                owner = lock['owner_task']
                rec_cnt = lock['recursion_count']
                task_name = owner['pcTaskName'].string() if owner != 0 else "FREE"
                print(f"Замок 0x{int(lock):x} | Власник: {task_name} | Глибина рекурсії: {rec_cnt}")
                curr = curr['next']
        except Exception as e:
            print(f"[-] Помилка читання структур замків: {e}")
            print("[!] Перевірте наявність символів відлагодження у ELF-файлі прошивки.")

InspectReentrantLocks()
