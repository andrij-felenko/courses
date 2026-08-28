int counter = 100;

template<typename T>
void execute_step() {
    if constexpr (int counter = sizeof(T); counter > 4) {
        // Тут counter дорівнює sizeof(T), а не 100
        process_large_type(counter);
    } else {
        // У гілці else локальний counter ТАКОЖ доступний і дорівнює sizeof(T)
        process_small_type(counter);
    }
}
