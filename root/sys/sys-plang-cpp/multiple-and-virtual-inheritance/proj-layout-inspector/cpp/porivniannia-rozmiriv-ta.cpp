int main() {
    std::cout << "=========================================================\n";
    std::cout << " ДІАГНОСТИЧНИЙ ІНСПЕКТОР РОЗКЛАДКИ ПАМ'ЯТІ C++\n";
    std::cout << "=========================================================\n\n";

    std::cout << "Порівняння розмірів типів (платформа 64-біт):\n";
    std::cout << "  sizeof(Device)          = " << std::setw(2) << sizeof(Device) << " B (vptr 8 B + id 4 B + pad 4 B)\n";
    std::cout << "  sizeof(AudioIn)         = " << std::setw(2) << sizeof(AudioIn) << " B (Device 16 B + rate 4 B + pad 4 B)\n";
    std::cout << "  sizeof(AudioOut)        = " << std::setw(2) << sizeof(AudioOut) << " B (Device 16 B + buf 4 B + pad 4 B)\n";
    std::cout << "  sizeof(AudioDuplexNV)   = " << std::setw(2) << sizeof(AudioDuplexNV)
              << " B (In 24 B + Out 24 B + flags 4 B + pad 4 B -> 56 B)\n";
    std::cout << "  ---------------------------------------------------------\n";
    std::cout << "  sizeof(VDevice)         = " << std::setw(2) << sizeof(VDevice) << " B\n";
    std::cout << "  sizeof(VirtualAudioIn)  = " << std::setw(2) << sizeof(VirtualAudioIn)
              << " B (vptr 8 B + rate 4 B + pad 4 B + VDevice 16 B -> 32 B)\n";
    std::cout << "  sizeof(VirtualAudioOut) = " << std::setw(2) << sizeof(VirtualAudioOut) << " B\n";
    std::cout << "  sizeof(AudioDuplexV)    = " << std::setw(2) << sizeof(AudioDuplexV)
              << " B (vptr_In 8 B + in_f 8 B + vptr_Out 8 B + out_f 8 B + flags 8 B + VDevice 16 B -> 56 B)\n\n";

    probe_pointer_adjustments();
    probe_state_duplication();
    probe_virtual_base_offsets();
    probe_side_casting();
    probe_construction_vtable_phases();
    benchmark_field_access();
    probe_empty_base_layouts();

    std::cout << "Усі діагностичні експерименти виконано успішно.\n";
    return 0;
}
