// 1. Первинний шаблон А (загальний)
template<typename T>
void execute(T x);

// 2. Повна спеціалізація первинного шаблону А для int*
template<>
void execute<int*>(int* x);

// 3. Первинний шаблон Б (перевантаження для вказівників)
template<typename T>
void execute(T* x);

int main() {
    int value = 100;
    int* ptr = &value;
    
    execute(ptr); // Який код виконається?
}
