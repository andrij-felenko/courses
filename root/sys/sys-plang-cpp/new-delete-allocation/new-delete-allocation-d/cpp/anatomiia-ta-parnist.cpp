// Виділення та звільнення у C++ через вирази new / delete
struct Device {
    int id;
    std::string buffer;

    Device(int device_id, std::size_t buf_size)
        : id(device_id), buffer(buf_size, '\0') {}
    ~Device() = default; // std::string звільнить свою пам'ять автоматично
};

// Вираз new: operator new(sizeof(Device)) + конструктор Device
Device* dev = new Device(1, 256);

// Вираз delete: деструктор ~Device() + operator delete(dev)
delete dev;
