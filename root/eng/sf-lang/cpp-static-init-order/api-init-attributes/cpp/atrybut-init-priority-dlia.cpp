#include <iostream>

class MemoryManager {
public:
    MemoryManager() { std::cout << "[INIT 150] Менеджер пам'яті готовий\n"; }
};

class TaskScheduler {
public:
    TaskScheduler() { std::cout << "[INIT 300] Планувальник задач готовий\n"; }
};

// Менше число = вищий пріоритет (виконується раніше)
MemoryManager g_mem_mgr [[gnu::init_priority(150)]];
TaskScheduler g_sched [[gnu::init_priority(300)]];
