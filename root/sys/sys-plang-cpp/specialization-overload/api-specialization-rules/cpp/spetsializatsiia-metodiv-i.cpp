template<typename T>
struct Processor {
    void process_data(T val) {
        // Загальний алгоритм
    }

    template<typename U>
    void transform(U extra);
};

// Повна спеціалізація конкретного методу первинного шаблону:
template<>
inline void Processor<int>::process_data(int val) {
    // Швидкий бітовий алгоритм виключно для Processor<int>
}

// Повна спеціалізація вкладеного шаблонного методу:
template<>
template<>
inline void Processor<double>::transform<int>(int extra) {
    // Реалізація для Processor<double>::transform<int>
}
