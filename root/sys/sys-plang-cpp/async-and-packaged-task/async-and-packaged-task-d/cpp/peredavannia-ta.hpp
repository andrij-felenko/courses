void update_data(std::string& data);
void process_unique(std::unique_ptr<Data> ptr);

std::string my_str = "hello";
auto my_ptr = std::make_unique<Data>();

// ПОМИЛКА КОМПІЛЯЦІЇ: async намагається передати rvalue-копію у lvalue-посилання!
// auto fut1 = std::async(std::launch::async, update_data, my_str);

// ПРАВИЛЬНО: використовуємо std::ref для явного передавання посилання
auto fut1 = std::async(std::launch::async, update_data, std::ref(my_str));

// ПРАВИЛЬНО: переміщуємо move-only об'єкти
auto fut2 = std::async(std::launch::async, process_unique, std::move(my_ptr));
