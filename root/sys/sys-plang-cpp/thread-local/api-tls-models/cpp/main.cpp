// Код користувача:
thread_local std::string per_thread_name = "worker-" + get_uuid();

// Псевдокод, який генерує компілятор (Clang/GCC Itanium ABI):
static thread_local bool __tls_guard_per_thread_name = false;
static thread_local char __tls_storage_per_thread_name[sizeof(std::string)];

std::string& __get_per_thread_name() {
    if (!__tls_guard_per_thread_name) {
        __tls_guard_per_thread_name = true;
        // 1. Виклик конструктора на сирій пам'яті (placement new)
        new (__tls_storage_per_thread_name) std::string("worker-" + get_uuid());
        // 2. Реєстрація деструктора в рантаймі потоку
        __cxa_thread_atexit(
            [](void* ptr) { reinterpret_cast<std::string*>(ptr)->~basic_string(); },
            __tls_storage_per_thread_name,
            &__dso_handle
        );
    }
    return *reinterpret_cast<std::string*>(__tls_storage_per_thread_name);
}
