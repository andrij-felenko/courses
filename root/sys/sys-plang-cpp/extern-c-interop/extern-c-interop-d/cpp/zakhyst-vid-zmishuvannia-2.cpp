extern "C" void engine_destroy(engine_t* engine) {
    if (!engine) return;
    try {
        // Відновлюємо володіння через unique_ptr:
        // оператор delete викличе деструктори EngineCore та його полів
        std::unique_ptr<engine_t> cleaner(engine);
    } catch (...) {
        // Захист межі C-ABI
    }
}
