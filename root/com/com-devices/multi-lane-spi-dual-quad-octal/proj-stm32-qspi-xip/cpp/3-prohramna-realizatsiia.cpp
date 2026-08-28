#include "stm32h7xx_hal.h"
#include <concepts>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

enum class QspiError : uint8_t {
    HardwareFault,
    Timeout,
    InvalidDevice,
    WriteProtected
};

class QspiXipController {
public:
    static constexpr uintptr_t FlashBaseAddress = 0x90000000U;
    static constexpr size_t    FlashSizeBytes   = 16 * 1024 * 1024; // 16 MB

    explicit QspiXipController(QUADSPI_TypeDef* instance = QUADSPI) noexcept
        : instance_(instance) {
        hqspi_.Instance = instance_;
    }

    ~QspiXipController() noexcept {
        if (is_mapped_) {
            HAL_QSPI_Abort(&hqspi_);
            HAL_QSPI_DeInit(&hqspi_);
        }
    }

    QspiXipController(const QspiXipController&) = delete;
    QspiXipController& operator=(const QspiXipController&) = delete;
    QspiXipController(QspiXipController&&) noexcept = default;
    QspiXipController& operator=(QspiXipController&&) noexcept = default;

    [[nodiscard]] std::expected<void, QspiError> initialize(uint8_t prescaler = 1) noexcept {
        hqspi_.Init.ClockPrescaler     = prescaler;
        hqspi_.Init.FifoThreshold      = 4;
        hqspi_.Init.SampleShifting     = QSPI_SAMPLE_SHIFTING_HALFCYCLE;
        hqspi_.Init.FlashSize          = 23; // 16 МБ (2^(23+1))
        hqspi_.Init.ChipSelectHighTime = QSPI_CS_HIGH_TIME_4_CYCLE;
        hqspi_.Init.ClockMode          = QSPI_CLOCK_MODE_0;
        hqspi_.Init.FlashID            = QSPI_FLASH_ID_1;
        hqspi_.Init.DualFlash          = QSPI_DUALFLASH_DISABLE;

        if (HAL_QSPI_Init(&hqspi_) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        if (auto res = enable_quad_mode(); !res) {
            return res;
        }

        if (auto res = enter_memory_mapped_mode(); !res) {
            return res;
        }

        is_mapped_ = true;
        return {};
    }

    [[nodiscard]] static std::span<const uint8_t> memory_view() noexcept {
        return {reinterpret_cast<const uint8_t*>(FlashBaseAddress), FlashSizeBytes};
    }

    template<typename T>
    [[nodiscard]] static const T* get_pointer_at(uintptr_t offset) noexcept {
        if (offset + sizeof(T) > FlashSizeBytes) return nullptr;
        return reinterpret_cast<const T*>(FlashBaseAddress + offset);
    }

private:
    static constexpr uint8_t CmdWriteEnable      = 0x06;
    static constexpr uint8_t CmdReadStatusReg1   = 0x05;
    static constexpr uint8_t CmdReadStatusReg2   = 0x35;
    static constexpr uint8_t CmdWriteStatusReg2  = 0x31;
    static constexpr uint8_t CmdFastReadQuadIo   = 0xEB;
    static constexpr uint8_t Status2QeBit        = (1U << 1);

    QUADSPI_TypeDef* instance_;
    QSPI_HandleTypeDef hqspi_{};
    bool is_mapped_{false};

    [[nodiscard]] std::expected<void, QspiError> wait_busy(uint32_t timeout_ms = 1000) noexcept {
        QSPI_CommandTypeDef cmd{};
        cmd.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
        cmd.Instruction       = CmdReadStatusReg1;
        cmd.AddressMode       = QSPI_ADDRESS_NONE;
        cmd.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
        cmd.DataMode          = QSPI_DATA_1_LINE;

        QSPI_AutoPollingTypeDef cfg{};
        cfg.Match           = 0x00;
        cfg.Mask            = 0x01;
        cfg.MatchMode       = QSPI_MATCH_MODE_AND;
        cfg.StatusBytesSize = 1;
        cfg.Interval        = 0x10;
        cfg.AutomaticStop   = QSPI_AUTOMATIC_STOP_ENABLE;

        if (HAL_QSPI_AutoPolling(&hqspi_, &cmd, &cfg, timeout_ms) != HAL_OK) {
            return std::unexpected(QspiError::Timeout);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, QspiError> enable_quad_mode() noexcept {
        QSPI_CommandTypeDef cmd{};
        cmd.InstructionMode = QSPI_INSTRUCTION_1_LINE;
        cmd.Instruction     = CmdReadStatusReg2;
        cmd.DataMode        = QSPI_DATA_1_LINE;
        cmd.NbData          = 1;

        uint8_t status2 = 0;
        if (HAL_QSPI_Command(&hqspi_, &cmd, 100) != HAL_OK ||
            HAL_QSPI_Receive(&hqspi_, &status2, 100) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        if (status2 & Status2QeBit) return {};

        cmd.Instruction = CmdWriteEnable;
        cmd.DataMode    = QSPI_DATA_NONE;
        if (HAL_QSPI_Command(&hqspi_, &cmd, 100) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        status2 |= Status2QeBit;
        cmd.Instruction = CmdWriteStatusReg2;
        cmd.DataMode    = QSPI_DATA_1_LINE;
        cmd.NbData      = 1;

        if (HAL_QSPI_Command(&hqspi_, &cmd, 100) != HAL_OK ||
            HAL_QSPI_Transmit(&hqspi_, &status2, 100) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        return wait_busy(1000);
    }

    [[nodiscard]] std::expected<void, QspiError> enter_memory_mapped_mode() noexcept {
        QSPI_CommandTypeDef cmd{};
        cmd.InstructionMode    = QSPI_INSTRUCTION_1_LINE;
        cmd.Instruction        = CmdFastReadQuadIo;
        cmd.AddressMode        = QSPI_ADDRESS_4_LINES;
        cmd.AddressSize        = QSPI_ADDRESS_24_BITS;
        cmd.AlternateByteMode  = QSPI_ALTERNATE_BYTES_4_LINES;
        cmd.AlternateBytesSize = QSPI_ALTERNATE_BYTES_8_BITS;
        cmd.AlternateBytes     = 0x20; // Continuous Read Mode
        cmd.DummyCycles        = 6;
        cmd.DataMode           = QSPI_DATA_4_LINES;
        cmd.SIOOMode           = QSPI_SIOO_INST_ONLY_FIRST_CMD;

        QSPI_MemoryMappedTypeDef cfg{};
        cfg.TimeOutActivation = QSPI_TIMEOUT_COUNTER_DISABLE;

        if (HAL_QSPI_MemoryMapped(&hqspi_, &cmd, &cfg) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }
        return {};
    }
};
