#include "stm32h7xx_hal.h"
#include <stdbool.h>
#include <stdint.h>

#define QSPI_FLASH_BASE_ADDR    0x90000000U
#define QSPI_FLASH_SIZE_BYTES   0x01000000U /* 16 МБайт (128 Мбіт) */

/* Опкоди Flash-пам'яті Winbond W25Q128JV */
#define CMD_WRITE_ENABLE        0x06
#define CMD_READ_STATUS_REG1    0x05
#define CMD_READ_STATUS_REG2    0x35
#define CMD_WRITE_STATUS_REG2   0x31
#define CMD_READ_JEDEC_ID       0x9F
#define CMD_FAST_READ_QUAD_IO   0xEB

#define STATUS2_QE_BIT          (1U << 1) /* Біт Quad Enable (S9) */

static QSPI_HandleTypeDef hqspi;

/**
 * @brief Очікування завершення внутрішньої операції Flash (WIP = 0)
 */
static HAL_StatusTypeDef qspi_wait_busy(uint32_t timeout_ms)
{
    QSPI_CommandTypeDef cmd = {0};
    QSPI_AutoPollingTypeDef cfg = {0};

    cmd.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
    cmd.Instruction       = CMD_READ_STATUS_REG1;
    cmd.AddressMode       = QSPI_ADDRESS_NONE;
    cmd.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
    cmd.DataMode          = QSPI_DATA_1_LINE;
    cmd.DummyCycles       = 0;
    cmd.DdrMode           = QSPI_DDR_MODE_DISABLE;
    cmd.SIOOMode          = QSPI_SIOO_INST_EVERY_CMD;

    /* Очікуємо, поки біт 0 (Write In Progress) регістра стану стане 0 */
    cfg.Match           = 0x00;
    cfg.Mask            = 0x01;
    cfg.MatchMode       = QSPI_MATCH_MODE_AND;
    cfg.StatusBytesSize = 1;
    cfg.Interval        = 0x10;
    cfg.AutomaticStop   = QSPI_AUTOMATIC_STOP_ENABLE;

    return HAL_QSPI_AutoPolling(&hqspi, &cmd, &cfg, timeout_ms);
}

/**
 * @brief Перевірка та увімкнення біта Quad Enable (QE)
 */
static HAL_StatusTypeDef qspi_enable_quad_mode(void)
{
    QSPI_CommandTypeDef cmd = {0};
    uint8_t status2 = 0;

    /* 1. Читаємо другий регістр стану */
    cmd.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
    cmd.Instruction       = CMD_READ_STATUS_REG2;
    cmd.AddressMode       = QSPI_ADDRESS_NONE;
    cmd.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
    cmd.DataMode          = QSPI_DATA_1_LINE;
    cmd.NbData            = 1;
    cmd.DummyCycles       = 0;

    if (HAL_QSPI_Command(&hqspi, &cmd, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;
    if (HAL_QSPI_Receive(&hqspi, &status2, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;

    /* Якщо біт QE вже встановлений — виходимо */
    if ((status2 & STATUS2_QE_BIT) != 0)
        return HAL_OK;

    /* 2. Надсилаємо Write Enable */
    cmd.Instruction = CMD_WRITE_ENABLE;
    cmd.DataMode    = QSPI_DATA_NONE;
    if (HAL_QSPI_Command(&hqspi, &cmd, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;

    /* 3. Записуємо оновлений Status Register 2 з встановленим бітом QE */
    status2 |= STATUS2_QE_BIT;
    cmd.Instruction = CMD_WRITE_STATUS_REG2;
    cmd.DataMode    = QSPI_DATA_1_LINE;
    cmd.NbData      = 1;

    if (HAL_QSPI_Command(&hqspi, &cmd, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;
    if (HAL_QSPI_Transmit(&hqspi, &status2, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;

    return qspi_wait_busy(1000);
}

/**
 * @brief Активація режиму Memory-Mapped (Execute-in-Place)
 */
HAL_StatusTypeDef qspi_init_memory_mapped(void)
{
    hqspi.Instance = QUADSPI;
    hqspi.Init.ClockPrescaler     = 1;          /* 200 МГц / (1 + 1) = 100 МГц */
    hqspi.Init.FifoThreshold      = 4;
    hqspi.Init.SampleShifting     = QSPI_SAMPLE_SHIFTING_HALFCYCLE;
    hqspi.Init.FlashSize          = 23;         /* 2^(23+1) = 2^24 = 16 МБайт */
    hqspi.Init.ChipSelectHighTime = QSPI_CS_HIGH_TIME_4_CYCLE;
    hqspi.Init.ClockMode          = QSPI_CLOCK_MODE_0;
    hqspi.Init.FlashID            = QSPI_FLASH_ID_1;
    hqspi.Init.DualFlash          = QSPI_DUALFLASH_DISABLE;

    if (HAL_QSPI_Init(&hqspi) != HAL_OK)
        return HAL_ERROR;

    if (qspi_enable_quad_mode() != HAL_OK)
        return HAL_ERROR;

    /* Налаштування команди швидкого читання Fast Read Quad I/O 1-4-4 */
    QSPI_CommandTypeDef s_command = {0};
    s_command.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
    s_command.Instruction       = CMD_FAST_READ_QUAD_IO;
    s_command.AddressMode       = QSPI_ADDRESS_4_LINES;
    s_command.AddressSize       = QSPI_ADDRESS_24_BITS;
    s_command.AlternateByteMode = QSPI_ALTERNATE_BYTES_4_LINES;
    s_command.AlternateBytesSize= QSPI_ALTERNATE_BYTES_8_BITS;
    s_command.AlternateBytes    = 0x20;         /* Режим Continuous Read */
    s_command.DummyCycles       = 6;            /* 6 dummy-тактів для 100 МГц */
    s_command.DataMode          = QSPI_DATA_4_LINES;
    s_command.DdrMode           = QSPI_DDR_MODE_DISABLE;
    s_command.SIOOMode          = QSPI_SIOO_INST_ONLY_FIRST_CMD;

    QSPI_MemoryMappedTypeDef s_mem_mapped_cfg = {0};
    s_mem_mapped_cfg.TimeOutActivation = QSPI_TIMEOUT_COUNTER_DISABLE;

    /* Переведення апаратного контролера у режим прямого відображення */
    return HAL_QSPI_MemoryMapped(&hqspi, &s_command, &s_mem_mapped_cfg);
}
