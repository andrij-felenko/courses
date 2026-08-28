#include <iostream>
#include <cassert>
#include <vector>

namespace emb::ml::test {

class SimFlash {
public:
    SimFlash() : memory_(2048 * 1024, 0xFF) {}

    bool read(uint32_t addr, std::span<uint8_t> dst) {
        if (addr + dst.size() > memory_.size()) return false;
        std::copy_n(memory_.data() + addr, dst.size(), dst.data());
        return true;
    }

    bool write(uint32_t addr, std::span<const uint8_t> src) {
        if (addr + src.size() > memory_.size()) return false;
        for (size_t i = 0; i < src.size(); ++i) {
            memory_[addr + i] &= src[i];
        }
        return true;
    }

    bool erase_sector(uint32_t sector_addr) {
        if (sector_addr + kFlashSectorSize > memory_.size()) return false;
        std::fill_n(memory_.data() + sector_addr, kFlashSectorSize, 0xFF);
        return true;
    }

    static SimFlash& instance() {
        static SimFlash sim;
        return sim;
    }

private:
    std::vector<uint8_t> memory_;
};

FlashDriver make_sim_driver() {
    return FlashDriver{
        .read = [](uint32_t addr, std::span<uint8_t> dst) {
            return SimFlash::instance().read(addr, dst);
        },
        .write = [](uint32_t addr, std::span<const uint8_t> src) {
            return SimFlash::instance().write(addr, src);
        },
        .erase_sector = [](uint32_t addr) {
            return SimFlash::instance().erase_sector(addr);
        }
    };
}

void run_simulation() {
    auto driver = make_sim_driver();
    OtaConfig config{
        .nv_meta_addr = 0x000D0000,
        .slot_addrs = {0x000D8000, 0x00158000},
        .max_sram_arena = 64 * 1024
    };

    OtaUpdater updater(driver, config);
    auto res = updater.init();
    assert(res.has_value());
    assert(updater.active_slot() == SlotId::SlotA);

    ModelHeader bad_hdr{};
    bad_hdr.magic = kModelMagic;
    bad_hdr.header_version = kHeaderVersion;
    bad_hdr.payload_size = 8192;
    bad_hdr.required_arena_size = 16 * 1024;

    auto hdr_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&bad_hdr), sizeof(bad_hdr));
    res = updater.process_chunk(0, hdr_bytes);
    assert(res.has_value());

    std::array<uint8_t, 256> payload_chunk{};
    payload_chunk.fill(0x55);
    uint32_t written = 0;
    while (written < bad_hdr.payload_size) {
        res = updater.process_chunk(sizeof(bad_hdr) + written, payload_chunk);
        assert(res.has_value());
        written += static_cast<uint32_t>(payload_chunk.size());
    }

    auto meta = updater.metadata();
    auto fin_res = finalize_and_stage(updater, driver, config, meta, updater.target_slot());
    assert(fin_res.has_value());
    assert(meta.active_slot == SlotId::SlotB);
    assert(meta.slot_state[1] == SlotState::Trial);

    auto self_test_fail = [](uint32_t) { return false; };

    assert(!boot_validate_or_rollback(driver, config, meta, self_test_fail));
    assert(meta.trial_boots_remaining == 2);

    assert(!boot_validate_or_rollback(driver, config, meta, self_test_fail));
    assert(meta.trial_boots_remaining == 1);

    assert(!boot_validate_or_rollback(driver, config, meta, self_test_fail));
    assert(meta.active_slot == SlotId::SlotA);
    assert(meta.slot_state[1] == SlotState::Failed);

    std::cout << "C++ симуляція OTA успішно підтвердила відкат на стабільний банк.\n";
}

} // namespace emb::ml::test
