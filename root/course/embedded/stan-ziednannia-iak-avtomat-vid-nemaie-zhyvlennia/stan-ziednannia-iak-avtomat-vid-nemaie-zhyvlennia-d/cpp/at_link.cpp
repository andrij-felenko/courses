#include "at_link.hpp"

#include <charconv>

namespace {

constexpr bool startsWith(std::string_view s, std::string_view prefix)
{
    return s.size() >= prefix.size() && s.substr(0, prefix.size()) == prefix;
}

/* Послідовне читання чисел із рядка відповіді: "+CEREG: 2,1" → 2, 1. */
class IntScanner {
public:
    explicit IntScanner(std::string_view s) : m_s(s) {}

    std::optional<int> next()
    {
        while (m_pos < m_s.size() && (m_s[m_pos] < '0' || m_s[m_pos] > '9') && m_s[m_pos] != '-') {
            ++m_pos;
        }
        if (m_pos >= m_s.size()) {
            return std::nullopt;
        }
        int value{};
        const auto [ptr, ec] = std::from_chars(m_s.data() + m_pos, m_s.data() + m_s.size(), value);
        if (ec != std::errc{}) {
            m_pos = m_s.size();
            return std::nullopt;
        }
        m_pos = static_cast<std::size_t>(ptr - m_s.data());
        return value;
    }

private:
    std::string_view m_s;
    std::size_t m_pos{0};
};

AtMessage classify(std::string_view line)
{
    AtMessage msg{};

    if (line == "OK") {
        msg.kind = MsgKind::Ok;
    } else if (line == "ERROR") {
        msg.kind = MsgKind::Error;
    } else if (startsWith(line, "+CME ERROR:") || startsWith(line, "+CMS ERROR:")) {
        msg.kind = MsgKind::CmeError;
        /* AT+CMEE=2 може дати текст замість числа — тоді код невідомий. */
        msg.value = IntScanner{line.substr(11)}.next().value_or(-1);
    } else if (startsWith(line, "+CPIN:")) {
        msg.kind = MsgKind::Cpin;
        if (line.find("READY") != std::string_view::npos) {
            msg.value = static_cast<int>(SimState::Ready);
        } else if (line.find("SIM PIN") != std::string_view::npos ||
                   line.find("SIM PUK") != std::string_view::npos) {
            msg.value = static_cast<int>(SimState::NeedPin);
        } else {
            msg.value = static_cast<int>(SimState::Absent); /* NOT INSERTED, SIM FAILURE */
        }
    } else if (startsWith(line, "+CREG:") || startsWith(line, "+CEREG:")) {
        /* URC має один аргумент, відповідь на "?" — два: <n>,<stat>. */
        IntScanner scan{line};
        const auto first = scan.next();
        const auto second = scan.next();
        msg.kind = MsgKind::Creg;
        msg.value = second.value_or(first.value_or(0));
    } else if (startsWith(line, "+CSQ:")) {
        const auto idx = IntScanner{line}.next();
        msg.kind = MsgKind::Csq;
        msg.value = (idx && *idx <= 31) ? (-113 + 2 * *idx) : kRssiUnknown;
    } else if (startsWith(line, "+CGPADDR:")) {
        /* Контекст IPv4: без крапок або 0.0.0.0 — це ще не адреса. */
        const bool valid = line.find('.') != std::string_view::npos &&
                           line.find("0.0.0.0") == std::string_view::npos;
        msg.kind = valid ? MsgKind::IpReady : MsgKind::Unknown;
    } else if (line == "CONNECT OK" || startsWith(line, "+CIPOPEN: 0,0")) {
        msg.kind = MsgKind::ConnectOk;
    } else if (line == "SEND OK") {
        msg.kind = MsgKind::SendOk;
    } else if (line.find("CLOSED") != std::string_view::npos) {
        msg.kind = MsgKind::Closed;
    } else if (line.find("DEACT") != std::string_view::npos) {
        msg.kind = MsgKind::PdpDeact;
    } else if (line == "RDY" || line == "+CFUN: 1" || startsWith(line, "*ATREADY")) {
        msg.kind = MsgKind::Boot;
    } else {
        msg.kind = MsgKind::Unknown; /* луна команд до ATE0, банери оператора */
    }
    return msg;
}

} // namespace

AtLink::AtLink(ModemHal& hal) : m_hal(hal)
{
    m_hal.rtsSet(true);
}

std::uint16_t AtLink::fill() const noexcept
{
    const auto head = m_head.load(std::memory_order_relaxed);
    const auto tail = m_tail.load(std::memory_order_relaxed);
    return static_cast<std::uint16_t>((head - tail) & kRingMask);
}

void AtLink::rxFromIsr(std::byte byte)
{
    const auto head = m_head.load(std::memory_order_relaxed);
    const auto next = static_cast<std::uint16_t>((head + 1) & kRingMask);

    if (next == m_tail.load(std::memory_order_acquire)) {
        /* Черга повна: втрачаємо ОДИН байт, а не всю чергу. */
        m_overflows.fetch_add(1, std::memory_order_relaxed);
        return;
    }
    m_ring[head] = byte;
    m_head.store(next, std::memory_order_release);

    if (m_rtsReady && fill() >= kHighWater) {
        m_rtsReady = false;
        m_hal.rtsSet(false); /* просимо модем зупинити потік */
    }
}

std::optional<std::byte> AtLink::pop()
{
    const auto tail = m_tail.load(std::memory_order_relaxed);
    if (tail == m_head.load(std::memory_order_acquire)) {
        return std::nullopt;
    }
    const std::byte value = m_ring[tail];
    m_tail.store(static_cast<std::uint16_t>((tail + 1) & kRingMask), std::memory_order_release);

    if (!m_rtsReady && fill() <= kLowWater) {
        m_rtsReady = true;
        m_hal.rtsSet(true);
    }
    return value;
}

std::optional<AtMessage> AtLink::poll()
{
    while (const auto raw = pop()) {
        const auto byte = static_cast<char>(*raw);

        if (m_dataWant > 0) { /* тіло пакета з сокета */
            if (m_dataLen < kDataMax) {
                m_data[m_dataLen++] = *raw;
            }
            if (--m_dataWant == 0) {
                AtMessage msg{};
                msg.kind = MsgKind::Data;
                msg.data = std::span<const std::byte>{m_data.data(), m_dataLen};
                m_dataLen = 0;
                return msg;
            }
            continue;
        }

        if (byte == '>' && m_lineLen == 0) { /* запрошення AT+CIPSEND */
            return AtMessage{MsgKind::Prompt, 0, {}};
        }
        if (byte == '\r') {
            continue;
        }
        if (byte == '\n') {
            if (m_lineLen == 0) {
                continue;
            }
            const std::string_view line{m_line.data(), m_lineLen};
            const AtMessage msg = classify(line);
            m_lineLen = 0;
            if (msg.kind != MsgKind::Unknown) {
                return msg;
            }
            continue;
        }
        /* Заголовок "+IPD,<len>:" закінчується двокрапкою, а не CRLF. */
        if (byte == ':' && m_lineLen >= 5 &&
            std::string_view{m_line.data(), 5} == "+IPD,") {
            const std::string_view header{m_line.data() + 5, m_lineLen - 5};
            const auto len = IntScanner{header}.next();
            m_lineLen = 0;
            if (len && *len > 0) {
                m_dataWant = static_cast<std::size_t>(*len); /* хвіст понад kDataMax відкинемо */
                m_dataLen = 0;
            }
            continue;
        }
        if (m_lineLen + 1 < kLineMax) {
            m_line[m_lineLen++] = byte;
        } else {
            m_lineLen = 0; /* рядок довший за буфер — викидаємо цілком */
        }
    }
    return std::nullopt;
}

void AtLink::sendLine(std::string_view cmd)
{
    m_hal.uartWrite(std::as_bytes(std::span{cmd.data(), cmd.size()}));
    static constexpr std::array<char, 2> kCrLf{'\r', '\n'};
    m_hal.uartWrite(std::as_bytes(std::span{kCrLf}));
}

void AtLink::sendRaw(std::span<const std::byte> data)
{
    m_hal.uartWrite(data);
}
