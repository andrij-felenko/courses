union GrantEntryV2 {
    struct FullPage {
        std::uint16_t flags;
        std::uint16_t domid;
        std::uint32_t pad0;
        std::uint64_t frame;     // 64-бітний MFN для ОЗП понад 16 ТіБ
    } full_page;

    struct SubPage {
        std::uint16_t flags;
        std::uint16_t domid;
        std::uint16_t page_off;  // Зміщення всередині сторінки в байтах
        std::uint16_t length;    // Довжина дозволеного фрагмента
        std::uint64_t frame;     // MFN сторінки, фрагмент якої відкрито
    } sub_page;
};
