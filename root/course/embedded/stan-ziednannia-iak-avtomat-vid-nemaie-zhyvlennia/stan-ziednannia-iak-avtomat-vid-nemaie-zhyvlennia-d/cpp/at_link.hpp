#pragma once

#include "modem_hal.hpp"

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

/* Рівень лінії: кільце UART, апаратний контроль потоку й неблокуючий
   розбір рядків. Про стани автомата не знає — віддає класифіковані
   повідомлення модема. */

enum class MsgKind : std::uint8_t {
    Ok,
    Error,     /* голий ERROR без коду */
    CmeError,  /* value = числовий код CME/CMS */
    Prompt,    /* '>' від AT+CIPSEND, без CRLF */
    Boot,      /* RDY — модем стартував САМ */
    Cpin,      /* value = SimState */
    Creg,      /* value = <stat> реєстрації */
    Csq,       /* value = рівень сигналу в дБм */
    IpReady,
    ConnectOk,
    SendOk,
    Closed,
    PdpDeact,
    Data,      /* тіло пакета з сокета (+IPD) */
    Unknown
};

enum class SimState : int { Ready = 0, NeedPin = 1, Absent = 2 };

inline constexpr std::int8_t kRssiUnknown = 127;

struct AtMessage {
    MsgKind kind{MsgKind::Unknown};
    int value{0};
    /* Дійсний до наступного виклику poll(): дивиться у буфер збірки. */
    std::span<const std::byte> data{};
};

class AtLink {
public:
    explicit AtLink(ModemHal& hal);

    /* Викликається з переривання UART: лише кладе байт і смикає RTS. */
    void rxFromIsr(std::byte byte);

    [[nodiscard]] std::optional<AtMessage> poll();

    void sendLine(std::string_view cmd); /* дописує CR LF */
    void sendRaw(std::span<const std::byte> data);

    [[nodiscard]] std::uint32_t overflows() const noexcept { return m_overflows.load(); }

private:
    static constexpr std::size_t kRingSize = 512;
    static constexpr std::uint16_t kRingMask = kRingSize - 1;
    static constexpr std::uint16_t kHighWater = (kRingSize * 4) / 5; /* 80 % */
    static constexpr std::uint16_t kLowWater = kRingSize / 2;
    static constexpr std::size_t kLineMax = 192;
    static constexpr std::size_t kDataMax = 512;

    [[nodiscard]] std::uint16_t fill() const noexcept;
    [[nodiscard]] std::optional<std::byte> pop();

    ModemHal& m_hal;

    std::array<std::byte, kRingSize> m_ring{};
    std::atomic<std::uint16_t> m_head{0};
    std::atomic<std::uint16_t> m_tail{0};
    std::atomic<std::uint32_t> m_overflows{0};
    bool m_rtsReady{true};

    std::array<char, kLineMax> m_line{};
    std::size_t m_lineLen{0};
    std::array<std::byte, kDataMax> m_data{};
    std::size_t m_dataLen{0};
    std::size_t m_dataWant{0};
};
