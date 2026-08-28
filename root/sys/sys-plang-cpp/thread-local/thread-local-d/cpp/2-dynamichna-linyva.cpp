// Сирцевий код на C++:
thread_local std::string per_thread_buffer = initialize_buffer();

// Еквівалентний псевдокод, що генерується компілятором (Itanium ABI):
static thread_local bool __tls_guard_per_thread_buffer = false;
static thread_local alignas(std::string) std::byte __tls_storage_buffer[sizeof(std::string)];

std::string& __get_per_thread_buffer() {
    if (!__tls_guard_per_thread_buffer) {
        __tls_guard_per_thread_buffer = true;
        // 1. Виклик конструктора на попередньо виділеній TLS-пам'яті
        ::new (static_cast<void*>(__tls_storage_buffer)) std::string(initialize_buffer());
        
        // 2. Реєстрація деструктора для поточного потоку
        __cxa_thread_atexit(
            [](void* ptr) { reinterpret_cast<std::string*>(ptr)->~basic_string(); },
            __tls_storage_buffer,
            &__dso_handle
        );
    }
    return *reinterpret_cast<std::string*>(__tls_storage_buffer);
}
