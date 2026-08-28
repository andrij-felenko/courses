#include <cstdint>
#include <cstddef>
#include <concepts>

struct FreeBlockHeader {
    FreeBlockHeader* next_free{nullptr};
    std::size_t size{0};

    [[nodiscard]] std::uint8_t* byte_end() noexcept {
        return reinterpret_cast<std::uint8_t*>(this) + size;
    }
};

class AddressOrderedFreeList {
public:
    void insert_and_coalesce(FreeBlockHeader* block_to_insert) noexcept {
        FreeBlockHeader* prev = &head_;

        // 1. Пошук позиції за фізичною адресою
        while (prev->next_free != nullptr && prev->next_free < block_to_insert) {
            prev = prev->next_free;
        }

        // 2. Злиття з лівим сусідом
        if (prev != &head_ && prev->byte_end() == reinterpret_cast<std::uint8_t*>(block_to_insert)) {
            prev->size += block_to_insert->size;
            block_to_insert = prev;
        } else {
            block_to_insert->next_free = prev->next_free;
            prev->next_free = block_to_insert;
        }

        // 3. Злиття з правим сусідом
        if (block_to_insert->next_free != nullptr &&
            block_to_insert->byte_end() == reinterpret_cast<std::uint8_t*>(block_to_insert->next_free)) {
            block_to_insert->size += block_to_insert->next_free->size;
            block_to_insert->next_free = block_to_insert->next_free->next_free;
        }
    }

private:
    FreeBlockHeader head_{};
};
