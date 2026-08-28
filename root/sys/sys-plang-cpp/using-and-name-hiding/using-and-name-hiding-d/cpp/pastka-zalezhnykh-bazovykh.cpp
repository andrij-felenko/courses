template <typename T>
struct BaseProcessor {
    void process_data() {
        std::cout << "Базова обробка даних\n";
    }
};

template <typename T>
struct DerivedProcessor : public BaseProcessor<T> {
    void execute() {
        // process_data(); // ✗ ПОМИЛКА: 'process_data' was not declared in this scope!
        
        // Спосіб 1: виклик через this-> (робить ім'я залежним від T)
        this->process_data(); // ✓ Працює
        
        // Спосіб 2: кваліфікований виклик (вимикає віртуальність!)
        BaseProcessor<T>::process_data(); // ✓ Працює, але без динамічного поліморфізму
    }

    // Спосіб 3 (найбільш ідіоматичний): явне using-оголошення
    using BaseProcessor<T>::process_data;

    void execute_clean() {
        process_data(); // ✓ Працює природно й зберігає віртуальність!
    }
};
