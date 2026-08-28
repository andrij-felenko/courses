#include <cstdint>
#include <cstddef>
#include <span>

constexpr std::size_t PAGE_SIZE = 4096;
constexpr std::uint16_t PAGE_FLAG_LEAF     = 0x01;
constexpr std::uint16_t PAGE_FLAG_ROOT     = 0x02;
constexpr std::uint16_t PAGE_FLAG_OVERFLOW = 0x04;

#pragma pack(push, 1)

/* Заголовок сторінки B-дерева (24 байти) */
struct PageHeader {
    std::uint64_t lsn;                 /* WAL Log Sequence Number */
    std::uint32_t page_id;             /* Номер сторінки в файлі */
    std::uint16_t flags;               /* Прапорці сторінки */
    std::uint16_t num_cells;           /* Кількість елементів */
    std::uint16_t free_space_offset;   /* Верхня межа слотів */
    std::uint16_t cells_start_offset;  /* Нижня межа комірок даних */
    std::uint32_t right_sibling_id;    /* Вказівник на праву сусідню сторінку */
};

using CellOffset = std::uint16_t;

/* Структура комірки внутрішнього вузла */
struct InternalCell {
    std::uint32_t child_page_id;       /* Вказівник на дочірній блок */
    std::uint16_t key_len;             /* Довжина ключа у байтах */

    [[nodiscard]] std::span<const std::uint8_t> key_bytes() const noexcept {
        const auto* ptr = reinterpret_cast<const std::uint8_t*>(this) + sizeof(*this);
        return {ptr, key_len};
    }
};

/* Структура комірки листка */
struct LeafCell {
    std::uint16_t key_len;             /* Довжина ключа у байтах */
    std::uint16_t val_len;             /* Довжина значення/payload у байтах */

    [[nodiscard]] std::span<const std::uint8_t> payload_bytes() const noexcept {
        const auto* ptr = reinterpret_cast<const std::uint8_t*>(this) + sizeof(*this);
        return {ptr, static_cast<std::size_t>(key_len) + val_len};
    }
};

#pragma pack(pop)
