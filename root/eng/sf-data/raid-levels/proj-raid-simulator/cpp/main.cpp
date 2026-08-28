#include <iostream>
#include <vector>
#include <array>
#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <algorithm>

constexpr size_t SECTOR_SIZE = 64;
constexpr size_t NUM_DISKS = 4;

enum class RaidError {
    DiskOffline,
    MultipleDisksFailed,
    InvalidSector
};

class VirtualDisk {
public:
    std::array<uint8_t, SECTOR_SIZE> data{};
    bool is_online{true};

    void fail() noexcept {
        is_online = false;
        data.fill(0);
    }
};

class Raid5Array {
private:
    std::array<VirtualDisk, NUM_DISKS> disks_;

    [[nodiscard]] static constexpr size_t get_parity_disk(size_t stripe_idx) noexcept {
        return (NUM_DISKS - 1) - (stripe_idx % NUM_DISKS);
    }

    static void xor_buffers(std::span<const uint8_t> src, std::span<uint8_t> dest) noexcept {
        for (size_t i = 0; i < dest.size(); ++i) {
            dest[i] ^= src[i];
        }
    }

public:
    Raid5Array() = default;

    [[nodiscard]] std::expected<void, RaidError> write_sector(size_t logical_sector, std::span<const uint8_t, SECTOR_SIZE> input) {
        const size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
        const size_t data_col = logical_sector % (NUM_DISKS - 1);
        const size_t parity_disk = get_parity_disk(stripe_idx);

        size_t target_disk = data_col;
        if (target_disk >= parity_disk) {
            ++target_disk;
        }

        if (!disks_[target_disk].is_online) {
            return std::unexpected(RaidError::DiskOffline);
        }

        std::copy(input.begin(), input.end(), disks_[target_disk].data.begin());

        // Recalculate parity across all data disks
        std::array<uint8_t, SECTOR_SIZE> new_parity{};
        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d == parity_disk) continue;
            xor_buffers(disks_[d].data, new_parity);
        }

        if (disks_[parity_disk].is_online) {
            disks_[parity_disk].data = new_parity;
        }

        return {};
    }

    [[nodiscard]] std::expected<std::array<uint8_t, SECTOR_SIZE>, RaidError> read_sector(size_t logical_sector) const {
        const size_t stripe_idx = logical_sector / (NUM_DISKS - 1);
        const size_t data_col = logical_sector % (NUM_DISKS - 1);
        const size_t parity_disk = get_parity_disk(stripe_idx);

        size_t target_disk = data_col;
        if (target_disk >= parity_disk) {
            ++target_disk;
        }

        // Direct read if target disk is healthy
        if (disks_[target_disk].is_online) {
            return disks_[target_disk].data;
        }

        // Degraded Mode: Reconstruct sector via XOR
        std::cout << "[C++] Degraded Mode: Reconstructing sector " << logical_sector << " via XOR...\n";
        std::array<uint8_t, SECTOR_SIZE> reconstructed{};

        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d == target_disk) continue;
            if (!disks_[d].is_online) {
                return std::unexpected(RaidError::MultipleDisksFailed);
            }
            xor_buffers(disks_[d].data, reconstructed);
        }

        return reconstructed;
    }

    void simulate_disk_failure(size_t disk_idx) {
        if (disk_idx < NUM_DISKS) {
            disks_[disk_idx].fail();
            std::cout << "[C++] ⚠️ Disk " << disk_idx << " FAILED!\n";
        }
    }

    [[nodiscard]] std::expected<void, RaidError> rebuild_disk(size_t failed_disk_idx) {
        if (disks_[failed_disk_idx].is_online) return {};

        std::cout << "[C++] 🔄 Rebuilding disk " << failed_disk_idx << "...\n";

        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d != failed_disk_idx && !disks_[d].is_online) {
                return std::unexpected(RaidError::MultipleDisksFailed);
            }
        }

        disks_[failed_disk_idx].data.fill(0);
        for (size_t d = 0; d < NUM_DISKS; ++d) {
            if (d == failed_disk_idx) continue;
            xor_buffers(disks_[d].data, disks_[failed_disk_idx].data);
        }

        disks_[failed_disk_idx].is_online = true;
        std::cout << "[C++] ✅ Disk " << failed_disk_idx << " rebuild complete!\n";
        return {};
    }
};

int main() {
    Raid5Array raid;

    std::array<uint8_t, SECTOR_SIZE> write_buf{};
    std::string_view msg = "Idiomatic C++23 RAID Engine";
    std::copy(msg.begin(), msg.end(), write_buf.begin());

    std::cout << "1. Writing sector 0...\n";
    if (auto res = raid.write_sector(0, write_buf); !res) {
        std::cerr << "Write failed!\n";
        return 1;
    }

    if (auto res = raid.read_sector(0)) {
        std::cout << "Read result: \"" << reinterpret_cast<const char*>(res->data()) << "\"\n\n";
    }

    std::cout << "2. Simulating drive failure on disk 0...\n";
    raid.simulate_disk_failure(0);

    std::cout << "3. Reading in degraded mode...\n";
    if (auto res = raid.read_sector(0)) {
        std::cout << "On-the-fly reconstruction: \"" << reinterpret_cast<const char*>(res->data()) << "\"\n\n";
    }

    std::cout << "4. Rebuilding array...\n";
    if (auto res = raid.rebuild_disk(0); !res) {
        std::cerr << "Rebuild failed!\n";
        return 1;
    }

    if (auto res = raid.read_sector(0)) {
        std::cout << "Post-rebuild read: \"" << reinterpret_cast<const char*>(res->data()) << "\"\n";
    }

    return 0;
}
