class SensorNode {
    int size_;
    int* buffer_;
public:
    // Помилка: buffer_ оголошено ПІСЛЯ size_, але якби buffer_ стояв першим у класі:
    SensorNode(int s) : buffer_(new int[size_]), size_(s) {
        // Якщо в класі buffer_ оголошено раніше за size_, компілятор спочатку виділить
        // buffer_ розміром size_ (який ще НЕ ініціалізований і містить сміття!),
        // а вже потім ініціалізує size_ числом s.
    }
};
