template<typename T>
class DynamicArray {
public:
    // Цей метод доступний лише тоді, коли тип T підтримує копіювання
    void push_back(const T& item) requires std::copyable<T> {
        // Копіювання елемента в масив
    }

    // Цей метод доступний для будь-якого переміщуваного типу
    void push_back(T&& item) requires std::movable<T> {
        // Переміщення елемента в масив
    }
};
