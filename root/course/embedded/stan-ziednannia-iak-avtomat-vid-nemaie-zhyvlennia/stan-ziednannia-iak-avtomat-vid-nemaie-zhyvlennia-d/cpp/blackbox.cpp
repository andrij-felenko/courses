#include "blackbox.hpp"

namespace {

constexpr std::uint32_t kMagic = 0x424C4B31; /* "BLK1" */

std::uint16_t crc16(std::span<const std::byte> data)
{
    std::uint16_t crc = 0xFFFF;

    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(static_cast<std::uint8_t>(b)) << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

void putU16(std::span<std::byte> out, std::uint16_t value)
{
    out[0] = std::byte{static_cast<std::uint8_t>(value & 0xFF)};
    out[1] = std::byte{static_cast<std::uint8_t>(value >> 8)};
}

} // namespace

BlackBox::BlackBox(ModemHal& hal) : m_hal(hal)
{
    if (!m_hal.nvRead(std::as_writable_bytes(std::span{&m_nv, 1}))) {
        resetStore();
        return;
    }
    /* Перший запуск або зіпсована комірка: краще порожній журнал, ніж сміття. */
    if (m_nv.magic != kMagic || m_nv.head >= kDepth || m_nv.count > kDepth ||
        m_nv.crc != computeCrc()) {
        resetStore();
    }
}

BlackBox::~BlackBox()
{
    flush();
}

void BlackBox::resetStore()
{
    m_nv = Store{};
    m_nv.magic = kMagic;
}

std::uint16_t BlackBox::computeCrc() const
{
    const auto body = crc16(std::as_bytes(std::span{m_nv.records}));
    const std::array<std::byte, 2> tail{std::byte{m_nv.head}, std::byte{m_nv.count}};
    return static_cast<std::uint16_t>(body ^ crc16(tail));
}

void BlackBox::record(std::uint8_t fromState, std::uint8_t toState, std::uint8_t eventId,
                      std::uint8_t retryCount, std::int8_t rssiDbm, std::uint16_t cmeCode,
                      std::uint16_t vbatMv)
{
    const auto uptime = std::chrono::duration_cast<std::chrono::milliseconds>(
        m_hal.now().time_since_epoch());

    m_nv.records[m_nv.head] = Record{
        static_cast<std::uint32_t>(uptime.count()),
        fromState, toState, eventId, retryCount, rssiDbm, cmeCode, vbatMv, {}
    };

    m_nv.head = static_cast<std::uint8_t>((m_nv.head + 1) % kDepth);
    if (m_nv.count < kDepth) {
        ++m_nv.count;
    }
    /* Кільце переповнилося — найстаріший запис затерто, і це нормально:
       цікавить остання аварія, а не вся історія приладу. */
}

void BlackBox::flush()
{
    m_nv.crc = computeCrc();
    (void)m_hal.nvWrite(std::as_bytes(std::span{&m_nv, 1}));
}

std::span<const std::byte> BlackBox::exportFrame(std::span<std::byte> out) const
{
    std::size_t written = 0;
    auto index = static_cast<std::size_t>((m_nv.head + kDepth - m_nv.count) % kDepth);

    for (std::size_t i = 0; i < m_nv.count; ++i) {
        if (written + kRecordSize > out.size()) {
            break; /* решта поїде наступним кадром */
        }
        const Record& r = m_nv.records[index];
        const auto slot = out.subspan(written, kRecordSize);

        /* На дроті розкладку структури не припускаємо: пакуємо поле за полем. */
        putU16(slot.subspan(0, 2), static_cast<std::uint16_t>(r.timestampMs & 0xFFFF));
        putU16(slot.subspan(2, 2), static_cast<std::uint16_t>(r.timestampMs >> 16));
        slot[4] = std::byte{r.fromState};
        slot[5] = std::byte{r.toState};
        slot[6] = std::byte{r.eventId};
        slot[7] = std::byte{r.retryCount};
        slot[8] = std::byte{static_cast<std::uint8_t>(r.rssiDbm)};
        putU16(slot.subspan(9, 2), r.cmeErrorCode);
        putU16(slot.subspan(11, 2), r.voltageVbatMv);
        slot[13] = std::byte{0};
        slot[14] = std::byte{0};
        slot[15] = std::byte{0};

        written += kRecordSize;
        index = (index + 1) % kDepth;
    }
    return out.first(written);
}

void BlackBox::markSent(std::size_t bytes)
{
    const auto sent = static_cast<std::uint8_t>(bytes / kRecordSize);

    m_nv.count = (sent >= m_nv.count) ? 0 : static_cast<std::uint8_t>(m_nv.count - sent);
    flush();
}
