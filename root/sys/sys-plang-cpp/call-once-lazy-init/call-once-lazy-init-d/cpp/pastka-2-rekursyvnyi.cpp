// ❌ ПОМИЛКА: взаємне блокування (Deadlock)
std::once_flag g_flag;

void init_part_two() {
    std::call_once(g_flag, []() {
        std::cout << "Крок 2\n";
    });
}

void init_part_one() {
    std::call_once(g_flag, []() {
        std::cout << "Крок 1\n";
        init_part_two(); // Рекурсивне звернення до того самого g_flag!
    });
}
