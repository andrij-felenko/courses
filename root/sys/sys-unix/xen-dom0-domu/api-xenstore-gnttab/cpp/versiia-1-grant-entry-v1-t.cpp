struct GrantEntryV1 {
    std::uint16_t flags; /* Прапорці доступу (GTF_permit_access, GTF_reading, GTF_writing) */
    std::uint16_t domid; /* ID домену, якому надається доступ (domid_t) */
    std::uint32_t frame; /* Machine Frame Number (MFN) фізичної сторінки ОЗП */
};

// Прапорці у вигляді константних виразів C++20
namespace GrantFlags {
    constexpr std::uint16_t Invalid        = 0U << 0; // Запис недійсний / вільний
    constexpr std::uint16_t PermitAccess   = 1U << 0; // Надано дозвіл на відображення сторінки
    constexpr std::uint16_t AcceptTransfer = 2U << 0; // Надано дозвіл на передачу власності сторінки
    constexpr std::uint16_t ReadOnly       = 1U << 2; // Дозвіл тільки для читання
    constexpr std::uint16_t Reading        = 1U << 3; // Встановив гіпервізор: домен мапить для читання
    constexpr std::uint16_t Writing        = 1U << 4; // Встановив гіпервізор: домен мапить для запису
}
