// Псевдокод того, що насправді генерує компілятор для static Config instance:
static uint64_t guard_flag = 0;
static alignas(Config) char instance_storage[sizeof(Config)];

if ((guard_flag & 0xFF) == 0) { // Швидка атомарна перевірка
    if (__cxa_guard_acquire(&guard_flag)) { // Захоплення системного м'ютекса
        try {
            new (instance_storage) Config();
            __cxa_guard_release(&guard_flag); // Позначення успішної ініціалізації
        } catch (...) {
            __cxa_guard_abort(&guard_flag);
            throw;
        }
    }
}
return *reinterpret_cast<Config*>(instance_storage);
