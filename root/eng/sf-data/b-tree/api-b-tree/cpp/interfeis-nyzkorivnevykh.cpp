#include <cstdint>
#include <span>
#include <optional>
#include <cstring>

class BTreePageDecoder {
    std::span<uint8_t, PAGE_SIZE> buffer_;
    PageHeader* header_;

public:
    explicit BTreePageDecoder(std::span<uint8_t, PAGE_SIZE> buffer)
        : buffer_(buffer), header_(reinterpret_cast<PageHeader*>(buffer.data())) {}

    [[nodiscard]] bool is_leaf() const noexcept {
        return (header_->flags & PAGE_FLAG_LEAF) != 0;
    }

    [[nodiscard]] uint16_t cell_count() const noexcept {
        return header_->num_cells;
    }

    /* Отримати зсув i-ї комірки з масиву слотів */
    [[nodiscard]] uint16_t get_cell_offset(uint16_t index) const {
        if (index >= header_->num_cells) {
            throw std::out_of_range("Індекс слота виходить за межі num_cells");
        }
        const auto* slot_array = reinterpret_cast<const CellOffset*>(
            buffer_.data() + sizeof(PageHeader)
        );
        return slot_array[index];
    }

    /* Обчислити обсяг вільного простору у сторінці */
    [[nodiscard]] uint16_t free_space() const noexcept {
        if (header_->cells_start_offset < header_->free_space_offset) {
            return 0;
        }
        return header_->cells_start_offset - header_->free_space_offset;
    }

    /* Додати комірку у сторінку з дефрагментацією за потреби */
    bool insert_cell(uint16_t index, std::span<const uint8_t> key, std::span<const uint8_t> payload) {
        uint16_t required_bytes = sizeof(CellOffset) + sizeof(LeafCell) + key.size() + payload.size();
        if (free_space() < required_bytes) {
            return false; /* Сторінка переповнена, вимагається split */
        }

        // Виділяємо простір для комірки з кінця сторінки
        header_->cells_start_offset -= (sizeof(LeafCell) + key.size() + payload.size());
        uint16_t new_cell_offset = header_->cells_start_offset;

        auto* leaf_cell = reinterpret_cast<LeafCell*>(buffer_.data() + new_cell_offset);
        leaf_cell->key_len = static_cast<uint16_t>(key.size());
        leaf_cell->val_len = static_cast<uint16_t>(payload.size());
        std::memcpy(leaf_cell->payload, key.data(), key.size());
        std::memcpy(leaf_cell->payload + key.size(), payload.data(), payload.size());

        // Вставляємо новий слот у масив слотів зі зсувом елементів
        auto* slot_array = reinterpret_cast<CellOffset*>(buffer_.data() + sizeof(PageHeader));
        for (int i = header_->num_cells; i > index; --i) {
            slot_array[i] = slot_array[i - 1];
        }
        slot_array[index] = new_cell_offset;

        header_->num_cells++;
        header_->free_space_offset += sizeof(CellOffset);
        return true;
    }
};
