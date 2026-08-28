void benchmark_field_access() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 6: Мікровимірювання часу доступу до полів\n";
    std::cout << "=========================================================\n";

    constexpr std::size_t iterations = 50'000'000;

    AudioDuplexNV nv_obj;
    AudioDuplexV  v_obj;

    // Вказівники на проміжні інтерфейси
    AudioIn*        nv_in_ptr = &nv_obj;
    VirtualAudioIn* v_in_ptr  = &v_obj;

    // 1. Тест невіртуального доступу
    auto start_nv = std::chrono::steady_clock::now();
    volatile std::uint32_t sink_nv = 0;
    for (std::size_t i = 0; i < iterations; ++i) {
        sink_nv = nv_in_ptr->sample_rate;
    }
    auto end_nv = std::chrono::steady_clock::now();
    const auto dur_nv = std::chrono::duration_cast<std::chrono::milliseconds>(end_nv - start_nv).count();

    // 2. Тест віртуального доступу до поля віртуальної бази
    auto start_v = std::chrono::steady_clock::now();
    volatile std::uint32_t sink_v = 0;
    for (std::size_t i = 0; i < iterations; ++i) {
        sink_v = v_in_ptr->device_id;
    }
    auto end_v = std::chrono::steady_clock::now();
    const auto dur_v = std::chrono::duration_cast<std::chrono::milliseconds>(end_v - start_v).count();

    std::cout << "Кількість ітерацій циклу: " << std::dec << iterations << '\n';
    std::cout << "  Час доступу до поля невіртуальної бази : " << dur_nv << " мс\n";
    std::cout << "  Час доступу до поля віртуальної бази    : " << dur_v  << " мс\n";

    if (dur_nv > 0) {
        std::cout << "  Співвідношення витрат часу             : x"
                  << std::fixed << std::setprecision(2) << (static_cast<double>(dur_v) / dur_nv) << '\n';
    }
    std::cout << '\n';
}
