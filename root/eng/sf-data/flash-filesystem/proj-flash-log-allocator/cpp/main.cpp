#include <cstdint>
#include <cstddef>
#include <vector>
#include <array>
#include <optional>
#include <span>
#include <algorithm>
#include <memory>
#include <stdexcept>

class FlashLogStore {
public:
    static constexpr size_t BlockSize = 4096;
    static constexpr size_t BlockCount = 8;
    static constexpr uint8_t MagicByte = 0xA5;

    enum class BlockState : uint8_t {
        Free   = 0xFF,
        Active = 0xAA,
        Full   = 0x55
    };

    enum class RecordStatus : uint8_t {
        Committed = 0x00,
        Invalid   = 0x55,
        Empty     = 0xFF
    };

    struct RecordHeader {
        uint8_t  magic{MagicByte};
        uint16_t record_id{0};
        uint16_t length{0};
        uint32_t sequence{0};
        RecordStatus status{RecordStatus::Committed};
        uint32_t crc32{0};
    } __attribute__((packed));

    struct BlockHeader {
        uint32_t erase_count{0};
        BlockState state{BlockState::Free};
        uint8_t reserved[3]{0xFF, 0xFF, 0xFF};
    } __attribute__((packed));

    FlashLogStore() {
        for (auto &blk : storage_) {
            blk.fill(0xFF);
            auto *bh = reinterpret_cast<BlockHeader *>(blk.data());
            bh->erase_count = 0;
            bh->state = BlockState::Free;
        }
    }

    bool write(uint16_t id, std::span<const uint8_t> data) {
        const size_t total_size = sizeof(RecordHeader) + data.size();
        if (total_size > BlockSize - sizeof(BlockHeader)) {
            return false;
        }

        if (!active_block_ || write_offset_ + total_size > BlockSize) {
            if (active_block_) {
                auto *bh = reinterpret_cast<BlockHeader *>(storage_[*active_block_].data());
                bh->state = BlockState::Full;
            }

            auto new_blk = allocate_block();
            if (!new_blk) {
                if (!collect_garbage()) return false;
                new_blk = allocate_block();
                if (!new_blk) return false;
            }

            active_block_ = new_blk;
            write_offset_ = sizeof(BlockHeader);
        }

        invalidate_older(id);

        RecordHeader rh;
        rh.magic = MagicByte;
        rh.record_id = id;
        rh.length = static_cast<uint16_t>(data.size());
        rh.sequence = global_sequence_++;
        rh.status = RecordStatus::Committed;
        rh.crc32 = calculate_crc32(data);

        auto &raw_block = storage_[*active_block_];
        std::copy_n(reinterpret_cast<const uint8_t *>(&rh), sizeof(rh), raw_block.begin() + write_offset_);
        std::copy(data.begin(), data.end(), raw_block.begin() + write_offset_ + sizeof(rh));

        write_offset_ += total_size;
        return true;
    }

    [[nodiscard]] std::optional<std::vector<uint8_t>> read(uint16_t id) const {
        uint32_t max_seq = 0;
        const RecordHeader *found_hdr = nullptr;
        const uint8_t *found_payload = nullptr;

        for (const auto &blk : storage_) {
            size_t off = sizeof(BlockHeader);
            while (off + sizeof(RecordHeader) <= BlockSize) {
                const auto *rh = reinterpret_cast<const RecordHeader *>(&blk[off]);
                if (rh->magic != MagicByte) break;

                if (rh->record_id == id && rh->status == RecordStatus::Committed && rh->sequence >= max_seq) {
                    const uint8_t *payload = &blk[off + sizeof(RecordHeader)];
                    if (calculate_crc32(std::span(payload, rh->length)) == rh->crc32) {
                        max_seq = rh->sequence;
                        found_hdr = rh;
                        found_payload = payload;
                    }
                }
                off += sizeof(RecordHeader) + rh->length;
            }
        }

        if (!found_hdr) return std::nullopt;
        return std::vector<uint8_t>(found_payload, found_payload + found_hdr->length);
    }

private:
    std::array<std::array<uint8_t, BlockSize>, BlockCount> storage_{};
    std::optional<size_t> active_block_{std::nullopt};
    size_t write_offset_{0};
    uint32_t global_sequence_{1};

    static uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (uint8_t b : data) {
            crc ^= b;
            for (int j = 0; j < 8; ++j) {
                crc = (crc & 1) ? ((crc >> 1) ^ 0xEDB88320) : (crc >> 1);
            }
        }
        return ~crc;
    }

    std::optional<size_t> allocate_block() {
        size_t best_idx = BlockCount;
        uint32_t min_erase = UINT32_MAX;

        for (size_t i = 0; i < BlockCount; ++i) {
            const auto *bh = reinterpret_cast<const BlockHeader *>(storage_[i].data());
            if (bh->state == BlockState::Free && bh->erase_count < min_erase) {
                min_erase = bh->erase_count;
                best_idx = i;
            }
        }

        if (best_idx < BlockCount) {
            auto *bh = reinterpret_cast<BlockHeader *>(storage_[best_idx].data());
            bh->state = BlockState::Active;
            return best_idx;
        }
        return std::nullopt;
    }

    void erase_block(size_t block_idx) {
        auto *bh = reinterpret_cast<BlockHeader *>(storage_[block_idx].data());
        uint32_t next_ec = bh->erase_count + 1;
        storage_[block_idx].fill(0xFF);
        bh->erase_count = next_ec;
        bh->state = BlockState::Free;
    }

    void invalidate_older(uint16_t id) {
        for (auto &blk : storage_) {
            size_t off = sizeof(BlockHeader);
            while (off + sizeof(RecordHeader) <= BlockSize) {
                auto *rh = reinterpret_cast<RecordHeader *>(&blk[off]);
                if (rh->magic != MagicByte) break;
                if (rh->record_id == id && rh->status == RecordStatus::Committed) {
                    rh->status = RecordStatus::Invalid;
                }
                off += sizeof(RecordHeader) + rh->length;
            }
        }
    }

    bool collect_garbage() {
        size_t victim_idx = BlockCount;
        size_t max_dead_bytes = 0;

        for (size_t b = 0; b < BlockCount; ++b) {
            if (active_block_ && b == *active_block_) continue;
            const auto *bh = reinterpret_cast<const BlockHeader *>(storage_[b].data());
            if (bh->state != BlockState::Full) continue;

            size_t off = sizeof(BlockHeader);
            size_t dead = 0;
            while (off + sizeof(RecordHeader) <= BlockSize) {
                const auto *rh = reinterpret_cast<const RecordHeader *>(&storage_[b][off]);
                if (rh->magic != MagicByte) break;
                if (rh->status == RecordStatus::Invalid) {
                    dead += sizeof(RecordHeader) + rh->length;
                }
                off += sizeof(RecordHeader) + rh->length;
            }

            if (dead > max_dead_bytes) {
                max_dead_bytes = dead;
                victim_idx = b;
            }
        }

        if (victim_idx >= BlockCount) return false;

        // Копіюємо валідні записи
        size_t off = sizeof(BlockHeader);
        while (off + sizeof(RecordHeader) <= BlockSize) {
            const auto *rh = reinterpret_cast<const RecordHeader *>(&storage_[victim_idx][off]);
            if (rh->magic != MagicByte) break;
            if (rh->status == RecordStatus::Committed) {
                const uint8_t *payload = &storage_[victim_idx][off + sizeof(RecordHeader)];
                write(rh->record_id, std::span(payload, rh->length));
            }
            off += sizeof(RecordHeader) + rh->length;
        }

        erase_block(victim_idx);
        return true;
    }
};
