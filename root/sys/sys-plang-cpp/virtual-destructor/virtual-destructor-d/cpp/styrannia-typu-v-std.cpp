struct BaseWithoutVirtual {
    ~BaseWithoutVirtual() = default; // Не віртуальний!
};

struct DerivedWithResource : BaseWithoutVirtual {
    int* data{new int[100]};
    ~DerivedWithResource() { delete[] data; }
};

// Створення shared_ptr:
std::shared_ptr<BaseWithoutVirtual> ptr = std::make_shared<DerivedWithResource>();
// При руйнуванні ptr деструктор ~DerivedWithResource() БУДЕ викликано!
