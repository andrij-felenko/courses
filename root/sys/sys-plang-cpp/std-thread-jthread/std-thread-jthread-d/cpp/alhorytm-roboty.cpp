void safe_process_file_data(const std::string& path) {
    // C++20: std::jthread гарантує авто-приєднання при вихід з функції
    std::jthread worker([path](std::stop_token st) {
        while (!st.stop_requested()) {
            // Виконання порції читання файлу
        }
    });

    std::vector<int> vec;
    int data = vec.at(100); // Кидає std::out_of_range!
    
    // Стек розгортається -> деструктор ~jthread() робить worker.request_stop() -> worker.join()
    // Потік зупиняється, програма НЕ падає, виняток безпечно перехоплюється вище!
}
