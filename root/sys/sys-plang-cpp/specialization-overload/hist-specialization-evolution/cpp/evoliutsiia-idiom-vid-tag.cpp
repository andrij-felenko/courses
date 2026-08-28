template<typename T>
struct ProcessorHelper {
    static void execute(const T& value) { /* Загальна реалізація */ }
};

template<typename T>
struct ProcessorHelper<T*> {
    static void execute(const T* value) { /* Для вказівників */ }
};

template<typename T>
void process(const T& value) {
    ProcessorHelper<T>::execute(value);
}
