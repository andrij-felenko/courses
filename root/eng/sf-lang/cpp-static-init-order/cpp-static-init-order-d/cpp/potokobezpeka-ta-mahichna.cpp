// Концептуальний асемблерний еквівалент, який компілятор генерує для static Logger s_instance:
Logger& Logger::instance() {
    static int guard_flag = 0;
    static char storage[sizeof(Logger)];

    if (__atomic_load_n(&guard_flag, __ATOMIC_ACQUIRE) == 0) {
        if (__cxa_guard_acquire(&guard_flag)) {
            try {
                new (storage) Logger("application.log");
                __cxa_guard_release(&guard_flag);
            } catch (...) {
                __cxa_guard_abort(&guard_flag);
                throw;
            }
        }
    }
    return *reinterpret_cast<Logger*>(storage);
}
