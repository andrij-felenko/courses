// Базовий клас бібліотеки версії 1.0
class CustomArray {
public:
    virtual void add(int item) {
        // Додає елемент у буфер...
    }

    virtual void addAll(const int* items, size_t count) {
        for (size_t i = 0; i < count; ++i) {
            add(items[i]); // Версія 1.0: addAll викликає add для кожного елемента
        }
    }
};

// Користувацький клас, який хоче рахувати кількість доданих елементів
class CountingArray : public CustomArray {
public:
    size_t added_count{0};

    void add(int item) override {
        added_count++;
        CustomArray::add(item);
    }

    void addAll(const int* items, size_t count) override {
        added_count += count;
        CustomArray::addAll(items, count);
    }
};
