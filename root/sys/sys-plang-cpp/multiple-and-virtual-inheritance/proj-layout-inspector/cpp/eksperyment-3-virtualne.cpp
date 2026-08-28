void probe_virtual_base_offsets() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 3: Читання vbase_offset з віртуальної таблиці\n";
    std::cout << "=========================================================\n";

    AudioDuplexV vduplex;
    dump_memory(&vduplex, sizeof(AudioDuplexV), "AudioDuplexV (із virtual public)");

    const auto addr_root = reinterpret_cast<std::uintptr_t>(&vduplex);
    const auto* vdev_ptr = static_cast<VDevice*>(&vduplex);
    const auto addr_vdev = reinterpret_cast<std::uintptr_t>(vdev_ptr);

    const std::ptrdiff_t physical_offset = static_cast<std::ptrdiff_t>(addr_vdev - addr_root);
    std::cout << "Фізичне зміщення спільного VDevice у пам'яті: +" << std::dec << physical_offset << " байтів\n";

    // ── Читання службових полів vtable за специфікацією Itanium C++ ABI ──
    // 1. Перші 8 байтів об'єкта — це vptr головної віртуальної таблиці
    auto** vptr_entry = *reinterpret_cast<std::ptrdiff_t***>(&vduplex);

    // 2. Структура віртуальної таблиці в пам'яті:
    //    vptr_entry[ 0] = адреса першого віртуального методу (вхідна точка vptr)
    //    vptr_entry[-1] = вказівник на структуру std::type_info (RTTI)
    //    vptr_entry[-2] = offset-to-top (зсув від поточної позиції до початку всього об'єкта)
    //    vptr_entry[-3] = vbase_offset (зсув від поточної позиції до віртуальної бази VDevice)
    const std::ptrdiff_t offset_to_top = reinterpret_cast<std::ptrdiff_t>(vptr_entry[-2]);
    const std::ptrdiff_t vbase_offset  = reinterpret_cast<std::ptrdiff_t>(vptr_entry[-3]);

    std::cout << "Прочитано з vtable[-2] (offset-to-top): " << std::dec << offset_to_top << " байтів\n";
    std::cout << "Прочитано з vtable[-3] (vbase_offset) : +" << std::dec << vbase_offset << " байтів\n\n";

    if (vbase_offset == physical_offset) {
        std::cout << ">> ПІДТВЕРДЖЕНО: Значення vbase_offset у таблиці збігається з фізичним зсувом!\n";
    } else {
        std::cout << ">> УВАГА: На поточній платформі розкладка vtable відрізняється від Itanium ABI.\n";
    }
    std::cout << '\n';
}
