template <typename T>
class FixedNetworkProcessor : public BaseProcessor<T> {
public:
    // ── Рішення 1: Явне використання this-> (Рекомендовано для методів) ──────
    void process_v1(const T& packet) {
        // Вказівник this має залежний тип FixedNetworkProcessor<T>*,
        // тому вираз this->initialize_hardware() стає залежним виразом.
        // Його пошук відкладається до Фази 2 і успішно знаходить метод у BaseProcessor<T>.
        this->initialize_hardware();
        std::cout << "Status: " << this->status_code << "\n";
    }

    // ── Рішення 2: Кваліфікація іменем базового класу ────────────────────────
    void process_v2(const T& packet) {
        // Запис BaseProcessor<T>:: містить параметр T, тому ім'я кваліфіковане і залежне.
        // УВАГА: Якщо initialize_hardware є VIRTUAL методом, такий запис ВИМИКАЄ
        // механізм віртуального виклику і здійснює прямий виклик функції базового класу!
        BaseProcessor<T>::initialize_hardware();
        std::cout << "Status: " << BaseProcessor<T>::status_code << "\n";
    }

    // ── Рішення 3: Введення імен через using (Рекомендовано для полів) ────────
    using BaseProcessor<T>::initialize_hardware;
    using BaseProcessor<T>::status_code;

    void process_v3(const T& packet) {
        // Завдяки using-оголошенню імена стають відомими у контексті класу на Фазі 1.
        // Виклики можна писати без префіксів у кожному методі класу.
        initialize_hardware();
        std::cout << "Status: " << status_code << "\n";
    }
};
