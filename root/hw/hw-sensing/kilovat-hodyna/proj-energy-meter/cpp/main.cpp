#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <expected>

namespace Metering {

inline constexpr uint32_t SampleRateHz = 8000;
inline constexpr uint32_t MainsFreqHz = 50;
inline constexpr uint32_t SamplesPerCycle = SampleRateHz / MainsFreqHz; // 160
inline constexpr uint32_t QuadratureDelay = SamplesPerCycle / 4;       // 40
inline constexpr size_t NvmSectorSlots = 8;
inline constexpr uint16_t NvmMagicWord = 0x5A4D;
inline constexpr int32_t AntiCreepPowerMw = 200;                       // 0.2 W
inline constexpr uint64_t MicroJoulesPerWh = 3'600'000'000ULL;

enum class Quadrant : uint8_t {
    None = 0,
    Q1_ImportInductive = 1, // +P, +Q
    Q2_ExportInductive = 2, // -P, +Q
    Q3_ExportCapacitive = 3, // -P, -Q
    Q4_ImportCapacitive = 4  // +P, -Q
};

enum class MeterError {
    CrcMismatch,
    StorageCorrupted,
    InvalidSample
};

struct EnergyRegisters {
    uint64_t actImportUj{0};
    uint64_t actExportUj{0};
    uint64_t reactIndUj{0};
    uint64_t reactCapUj{0};

    uint32_t actImportWh{0};
    uint32_t actExportWh{0};
    uint32_t reactIndVarh{0};
    uint32_t reactCapVarh{0};
};

struct alignas(4) NvmSlot {
    uint16_t magic{NvmMagicWord};
    uint16_t reserved{0};
    uint32_t seqId{0};
    uint32_t actImportWh{0};
    uint32_t actExportWh{0};
    uint32_t reactIndVarh{0};
    uint32_t reactCapVarh{0};
    uint16_t crc16{0};

    [[nodiscard]] static constexpr uint16_t calculateCrc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int b = 0; b < 8; ++b) {
                crc = (crc & 0x8000) ? static_cast<uint16_t>((crc << 1) ^ 0x1021) : static_cast<uint16_t>(crc << 1);
            }
        }
        return crc;
    }
};

class FourQuadrantEnergyEngine {
public:
    constexpr FourQuadrantEnergyEngine() noexcept {
        initStorage();
    }

    void processSample(int32_t vMv, int32_t iMa) noexcept {
        // 1. Квадратурний буфер затримки напруги на 90 градусів
        int32_t vDelayed = vDelayBuf_[delayIdx_];
        vDelayBuf_[delayIdx_] = vMv;
        delayIdx_ = (delayIdx_ + 1) % QuadratureDelay;

        // 2. Миттєві добутки (мВ * мА = мкВт)
        int64_t pInst = static_cast<int64_t>(vMv) * iMa;
        int64_t qInst = static_cast<int64_t>(vDelayed) * iMa;

        sumVsq_ += static_cast<int64_t>(vMv) * vMv;
        sumIsq_ += static_cast<int64_t>(iMa) * iMa;
        sumPinst_ += pInst;
        sumQinst_ += qInst;
        ++sampleCount_;

        // 3. Дискретне накопичення енергії кожні 125 мкс
        int64_t deP = pInst / SampleRateHz;
        int64_t deQ = qInst / SampleRateHz;

        if (pInst > static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.actImportUj += static_cast<uint64_t>(deP);
        } else if (pInst < -static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.actExportUj += static_cast<uint64_t>(-deP);
        }

        if (qInst > static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.reactIndUj += static_cast<uint64_t>(deQ);
        } else if (qInst < -static_cast<int64_t>(AntiCreepPowerMw) * 1000) {
            regs_.reactCapUj += static_cast<uint64_t>(-deQ);
        }

        // Перенесення ват-годин (квант 3.6 GJ)
        accumulateWh(regs_.actImportUj, regs_.actImportWh);
        accumulateWh(regs_.actExportUj, regs_.actExportWh);
        accumulateWh(regs_.reactIndUj, regs_.reactIndVarh);
        accumulateWh(regs_.reactCapUj, regs_.reactCapVarh);

        // 4. Фінал періоду 20 мс
        if (sampleCount_ >= SamplesPerCycle) {
            pActiveMw_ = static_cast<int32_t>(sumPinst_ / static_cast<int64_t>(sampleCount_) / 1000);
            qReactiveMvar_ = static_cast<int32_t>(sumQinst_ / static_cast<int64_t>(sampleCount_) / 1000);

            if (pActiveMw_ >= 0 && qReactiveMvar_ >= 0) {
                curQuadrant_ = Quadrant::Q1_ImportInductive;
            } else if (pActiveMw_ < 0 && qReactiveMvar_ >= 0) {
                curQuadrant_ = Quadrant::Q2_ExportInductive;
            } else if (pActiveMw_ < 0 && qReactiveMvar_ < 0) {
                curQuadrant_ = Quadrant::Q3_ExportCapacitive;
            } else {
                curQuadrant_ = Quadrant::Q4_ImportCapacitive;
            }

            sumVsq_ = 0;
            sumIsq_ = 0;
            sumPinst_ = 0;
            sumQinst_ = 0;
            sampleCount_ = 0;
        }
    }

    [[nodiscard]] std::expected<void, MeterError> commitToNvm() noexcept {
        uint32_t nextSeq = nvmLastSavedSeq_ + 1;
        size_t slotIdx = nextSeq % NvmSectorSlots;
        auto& slot = storage_[slotIdx];

        slot.magic = NvmMagicWord;
        slot.reserved = 0;
        slot.seqId = nextSeq;
        slot.actImportWh = regs_.actImportWh;
        slot.actExportWh = regs_.actExportWh;
        slot.reactIndVarh = regs_.reactIndVarh;
        slot.reactCapVarh = regs_.reactCapVarh;

        auto rawSpan = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&slot), sizeof(NvmSlot) - sizeof(uint16_t));
        slot.crc16 = NvmSlot::calculateCrc(rawSpan);

        nvmLastSavedSeq_ = nextSeq;
        return {};
    }

    [[nodiscard]] const EnergyRegisters& registers() const noexcept { return regs_; }
    [[nodiscard]] Quadrant currentQuadrant() const noexcept { return curQuadrant_; }
    [[nodiscard]] int32_t activePowerMw() const noexcept { return pActiveMw_; }
    [[nodiscard]] int32_t reactivePowerMvar() const noexcept { return qReactiveMvar_; }

private:
    static constexpr void accumulateWh(uint64_t& uj, uint32_t& wh) noexcept {
        if (uj >= MicroJoulesPerWh) {
            wh += static_cast<uint32_t>(uj / MicroJoulesPerWh);
            uj %= MicroJoulesPerWh;
        }
    }

    void initStorage() noexcept {
        uint32_t maxSeq = 0;
        std::optional<size_t> bestSlot;

        for (size_t s = 0; s < NvmSectorSlots; ++s) {
            const auto& slot = storage_[s];
            if (slot.magic == NvmMagicWord) {
                auto rawSpan = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&slot), sizeof(NvmSlot) - sizeof(uint16_t));
                if (NvmSlot::calculateCrc(rawSpan) == slot.crc16 && slot.seqId >= maxSeq) {
                    maxSeq = slot.seqId;
                    bestSlot = s;
                }
            }
        }

        if (bestSlot) {
            const auto& slot = storage_[*bestSlot];
            regs_.actImportWh = slot.actImportWh;
            regs_.actExportWh = slot.actExportWh;
            regs_.reactIndVarh = slot.reactIndVarh;
            regs_.reactCapVarh = slot.reactCapVarh;
            nvmLastSavedSeq_ = slot.seqId;
        }
    }

    std::array<int32_t, QuadratureDelay> vDelayBuf_{};
    size_t delayIdx_{0};

    int64_t sumVsq_{0};
    int64_t sumIsq_{0};
    int64_t sumPinst_{0};
    int64_t sumQinst_{0};
    uint32_t sampleCount_{0};

    int32_t pActiveMw_{0};
    int32_t qReactiveMvar_{0};
    Quadrant curQuadrant_{Quadrant::None};

    EnergyRegisters regs_{};
    uint32_t nvmLastSavedSeq_{0};
    std::array<NvmSlot, NvmSectorSlots> storage_{};
};

} // namespace Metering
