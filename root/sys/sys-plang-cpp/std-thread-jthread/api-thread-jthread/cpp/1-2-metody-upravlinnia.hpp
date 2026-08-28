// Перевірка активності потоку
bool joinable() const noexcept;

// Блокуюче очікування завершення потоку
void join();

// Асинхронне від'єднання потоку від C++ об'єкта
void detach();

// Отримання унікального ідентифікатора потоку
std::thread::id get_id() const noexcept;

// Отримання платформно-залежного системного дескриптора
native_handle_type native_handle();

// Оцінка кількості логічних ядер апаратного забезпечення
static unsigned int hardware_concurrency() noexcept;
