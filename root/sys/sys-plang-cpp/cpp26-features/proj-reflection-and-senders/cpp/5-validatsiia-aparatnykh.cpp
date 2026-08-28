template <typename T>
consteval bool validate_dma_layout() {
    constexpr auto type_meta = ^^T;
    constexpr auto members = std::meta::nonstatic_data_members_of(type_meta);

    // Перевірка 1: усі поля повинні бути публічними
    for (auto member : members) {
        if (!std::meta::is_public(member)) {
            return false;
        }
    }

    // Перевірка 2: тип повинен бути тривіально копійованим
    if (!std::is_trivially_copyable_v<T>) {
        return false;
    }

    return true;
}

struct DmaPacketHeader {
    uint32_t source_address;
    uint32_t destination_address;
    uint16_t payload_length;
    uint16_t flags;
};

// Компіляторний захист від помилок у драйвері
static_assert(validate_dma_layout<DmaPacketHeader>(), "DmaPacketHeader не відповідає вимогам DMA!");
