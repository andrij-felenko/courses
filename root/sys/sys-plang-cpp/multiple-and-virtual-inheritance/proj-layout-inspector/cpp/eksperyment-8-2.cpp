void probe_empty_base_layouts() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 8: Оптимізація порожніх баз (EBO)\n";
    std::cout << "=========================================================\n";

    std::cout << "Розмір порожньої структури sizeof(EmptyTag1): " << sizeof(EmptyTag1) << " B\n";
    std::cout << "Розмір CombinedTags (3 порожні бази + uint32): " << sizeof(CombinedTags)
              << " B (EBO обнулило розмір усіх трьох баз!)\n";
    std::cout << "Розмір TwoSameEmptyBases (2 різні порожні бази): " << sizeof(TwoSameEmptyBases)
              << " B (мінімальний розмір 1 байт)\n";
    std::cout << "Розмір CollisionEmptyBases (колізія адрес однакового типу): " << sizeof(CollisionEmptyBases)
              << " B (EBO не змогло застосуватися через вимогу унікальності адрес)\n\n";
}
