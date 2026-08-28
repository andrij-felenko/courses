// Функція, яка зациклюється (імітує незупинку)
void infinite_loop() {
    while (true) {} 
}

// Генератор обгортки (мапове зведення)
// Він бере функцію `suspect` і перетворює її на нову функцію `wrapper`.
std::function<int(int)> create_rice_wrapper(const std::function<void()>& suspect) {
    return [suspect](int y) -> int {
        // Крок 1: запустити підозрілу функцію
        suspect(); 
        
        // Крок 2: якщо вона завершилась, завжди повертаємо 42
        return 42;
    };
}
