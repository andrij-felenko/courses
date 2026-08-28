class DangerousOwner {
    int* buffer_a_;
    int* buffer_b_;
public:
    DangerousOwner() {
        buffer_a_ = new int[1000]; // 1. Успішно виділено пам'ять
        buffer_b_ = new int[5000]; // 2. Якщо тут виникає std::bad_alloc, конструктор обривається!
    }

    ~DangerousOwner() {
        // Цей деструктор НІКОЛИ не виконається при збої на другому new!
        // Пам'ять buffer_a_ витікає назавжди.
        delete[] buffer_a_;
        delete[] buffer_b_;
    }
};
