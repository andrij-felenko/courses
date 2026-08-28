struct alignas(32) Vector4D {
    float data[8];
    Vector4D(float val) {
        for (int i = 0; i < 8; ++i) data[i] = val;
    }
};

class TrackedResource {
public:
    TrackedResource(std::string name) : name_(std::move(name)) {
        std::cout << "  [+] Створено: " << name_ << " за адресою " << this << "\n";
    }

    ~TrackedResource() {
        std::cout << "  [-] Знищено:  " << name_ << " за адресою " << this << "\n";
    }

    const std::string& name() const { return name_; }

private:
    std::string name_;
};

int main() {
    std::cout << "=== Ініціалізація монотонної арени на 4096 байтів ===\n";
    MonotonicArena arena(4096);

    std::cout << "\n1. Створення об'єкта з надмірним вирівнюванням alignas(32):\n";
    auto* vec = arena.emplace<Vector4D>(3.14f);
    std::uintptr_t vec_addr = reinterpret_cast<std::uintptr_t>(vec);
    std::cout << "  Адреса Vector4D: 0x" << std::hex << vec_addr << std::dec << "\n";
    std::cout << "  Вирівняно по 32: " << (vec_addr % 32 == 0 ? "ТАК" : "НІ") << "\n";

    std::cout << "\n2. Створення тривіальних чисел (без виклику деструкторів):\n";
    int* num = arena.emplace<int>(42);
    double* dbl = arena.emplace<double>(2.71828);
    std::cout << "  int:    " << *num << " за адресою " << num << " (align: " << (reinterpret_cast<uintptr_t>(num) % 4 == 0) << ")\n";
    std::cout << "  double: " << *dbl << " за адресою " << dbl << " (align: " << (reinterpret_cast<uintptr_t>(dbl) % 8 == 0) << ")\n";

    std::cout << "\n3. Створення об'єктів з нетривіальними деструкторами:\n";
    {
        arena.emplace<TrackedResource>("Перший ресурс (HTTP Session)");
        arena.emplace<TrackedResource>("Другий ресурс (DB Transaction)");
        arena.emplace<TrackedResource>("Третій ресурс (File Handle)");
    }

    std::cout << "\nВикористано пам'яті в арені: " << arena.bytes_used() << " байтів\n";

    std::cout << "\n4. Скидання арени (виклик деструкторів у зворотному порядку LIFO):\n";
    arena.reset();

    std::cout << "\nПісля reset() використано пам'яті: " << arena.bytes_used() << " байтів\n";
    std::cout << "=== Завершення програми ===\n";
}
