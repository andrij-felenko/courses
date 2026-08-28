// CrashDump.cpp — реалізація діагностичного реєстратора на C++
#include "CrashDump.hpp"
#include <cstring>
#include <algorithm>

namespace Fault {

namespace {
    // Апаратні адреси STM32 та ARM Cortex-M SCB
    constexpr uintptr_t ScbBase   = 0xE000ED00U;
    volatile uint32_t& scbCfsr    = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x28U);
    volatile uint32_t& scbHfsr    = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x2CU);
    volatile uint32_t& scbMmfar   = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x34U);
    volatile uint32_t& scbBfar    = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x38U);
    volatile uint32_t& scbAircr   = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x0CU);

    constexpr uintptr_t RccCsrAddr = 0x40023874U;
    volatile uint32_t& rccCsr     = *reinterpret_cast<volatile uint32_t*>(RccCsrAddr);

    constexpr uint32_t RccRmvfBit = 1U << 24;
    constexpr uint32_t RccBorBit  = 1U << 25;
    constexpr uint32_t RccPinBit  = 1U << 26;
    constexpr uint32_t RccPorBit  = 1U << 27;
    constexpr uint32_t RccSftBit  = 1U << 28;
    constexpr uint32_t RccIwdgBit = 1U << 29;
    constexpr uint32_t RccWwdgBit = 1U << 30;

    // Змінна дампу в Retention RAM
    __attribute__((section(".noinit"))) CrashRecord g_persistentRecord;
    uint32_t g_rawCsr = 0;
    ResetCause g_bootCause = ResetCause::Unknown;
}

uint32_t BlackBox::calculateCrc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (size_t bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

void BlackBox::earlyInit() noexcept {
    g_rawCsr = rccCsr;
    rccCsr |= RccRmvfBit; // Очищення липких прапорців

    if (hasValidRecord()) {
        g_bootCause = g_persistentRecord.cause;
        return;
    }

    if (g_rawCsr & RccBorBit) {
        g_bootCause = ResetCause::Brownout;
    } else if (g_rawCsr & RccPorBit) {
        g_bootCause = ResetCause::ColdBoot;
    } else if ((g_rawCsr & RccIwdgBit) || (g_rawCsr & RccWwdgBit)) {
        g_bootCause = ResetCause::Watchdog;
    } else if (g_rawCsr & RccSftBit) {
        g_bootCause = ResetCause::Software;
    } else if (g_rawCsr & RccPinBit) {
        g_bootCause = ResetCause::PinReset;
    } else {
        g_bootCause = ResetCause::Unknown;
    }
}

bool BlackBox::hasValidRecord() noexcept {
    if (g_persistentRecord.magic != CrashRecord::MagicValue) {
        return false;
    }
    const auto payload = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_persistentRecord),
        sizeof(CrashRecord) - sizeof(uint32_t)
    );
    return g_persistentRecord.crc32 == calculateCrc32(payload);
}

const CrashRecord& BlackBox::getRecord() noexcept {
    return g_persistentRecord;
}

void BlackBox::clear() noexcept {
    g_persistentRecord.magic = 0;
    g_persistentRecord.crc32 = 0;
}

void BlackBox::reportAssert(std::string_view file, uint32_t line) noexcept {
    asm volatile("cpsid i" ::: "memory");

    g_persistentRecord.magic = CrashRecord::MagicValue;
    g_persistentRecord.rawRccCsr = g_rawCsr;
    g_persistentRecord.cause = ResetCause::Software;
    g_persistentRecord.uptimeMs = 0;

    g_persistentRecord.cfsr = 0;
    g_persistentRecord.hfsr = 0;
    g_persistentRecord.bfar = 0;
    g_persistentRecord.mmfar = 0;

    const size_t copyLen = std::min(file.size(), g_persistentRecord.assertFile.size() - 1);
    std::memcpy(g_persistentRecord.assertFile.data(), file.data(), copyLen);
    g_persistentRecord.assertFile[copyLen] = '\0';
    g_persistentRecord.assertLine = line;

    const auto payload = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_persistentRecord),
        sizeof(CrashRecord) - sizeof(uint32_t)
    );
    g_persistentRecord.crc32 = calculateCrc32(payload);

    asm volatile("dsb" ::: "memory");
    scbAircr = 0x05FA0000U | (1U << 2);
    while (true) { }
}

} // namespace Fault

// C++ зв'язка з асемблерним трампліном
extern "C" void prv_c_hardfault_handler(const uint32_t* stackFrame, uint32_t excReturn) {
    asm volatile("cpsid i" ::: "memory");

    using namespace Fault;
    g_persistentRecord.magic = CrashRecord::MagicValue;
    g_persistentRecord.rawRccCsr = g_rawCsr;
    g_persistentRecord.cause = ResetCause::HardFault;
    g_persistentRecord.uptimeMs = 0;

    g_persistentRecord.r0   = stackFrame[0];
    g_persistentRecord.r1   = stackFrame[1];
    g_persistentRecord.r2   = stackFrame[2];
    g_persistentRecord.r3   = stackFrame[3];
    g_persistentRecord.r12  = stackFrame[4];
    g_persistentRecord.lr   = stackFrame[5];
    g_persistentRecord.pc   = stackFrame[6];
    g_persistentRecord.xpsr = stackFrame[7];

    g_persistentRecord.cfsr  = scbCfsr;
    g_persistentRecord.hfsr  = scbHfsr;
    g_persistentRecord.bfar  = scbBfar;
    g_persistentRecord.mmfar = scbMmfar;
    g_persistentRecord.excReturn = excReturn;

    for (size_t i = 0; i < CrashRecord::StackWordsCount; ++i) {
        g_persistentRecord.stackDump[i] = stackFrame[i];
    }

    g_persistentRecord.assertFile[0] = '\0';
    g_persistentRecord.assertLine = 0;

    const auto payload = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_persistentRecord),
        sizeof(CrashRecord) - sizeof(uint32_t)
    );
    g_persistentRecord.crc32 = BlackBox::calculateCrc32(payload);

    asm volatile("dsb" ::: "memory");
    scbAircr = 0x05FA0000U | (1U << 2);
    while (true) { }
}
