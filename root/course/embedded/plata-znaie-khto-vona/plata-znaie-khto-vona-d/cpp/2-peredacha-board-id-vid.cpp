/* Структура поштової скриньки в спільній пам'яті SRAM */
struct BootMailbox {
    uint32_t magic{0x424F5244}; /* "BORD" */
    uint16_t board_rev{0};      /* Зчитана ревізія */
    uint16_t crc16{0};          /* Контрольна сума */

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return magic == 0x424F5244;
    }
};
