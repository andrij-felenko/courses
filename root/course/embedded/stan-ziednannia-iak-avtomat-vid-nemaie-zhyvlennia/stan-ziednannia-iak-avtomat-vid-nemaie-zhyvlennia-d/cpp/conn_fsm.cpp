#include "conn_fsm.hpp"

#include <algorithm>
#include <array>
#include <charconv>
#include <string_view>
#include <utility>

using namespace std::chrono_literals;

namespace {

/* Параметри вузла зашиті навмисно: це один конкретний прилад, а не бібліотека. */
constexpr std::string_view kApn = "iot.provider.apn";
constexpr std::string_view kSimPin = "0000";
constexpr std::string_view kClientId = "well-042";
constexpr std::string_view kUser = "well-042";
constexpr std::string_view kPassword = "s3cret";
constexpr std::string_view kTopic = "telemetry/well-042";
constexpr auto kKeepAlive = 60s;
constexpr bool kPsmEnabled = true; /* модуль уміє PSM за 3GPP Rel.12 */

constexpr auto kVbatSettle = 200ms;
constexpr auto kPwrkeyPulse = 1200ms;
constexpr auto kStatusWait = 5s;
constexpr auto kAtProbe = 500ms;
constexpr auto kAtCommand = 3s;
constexpr auto kSimTimeout = 10s;
constexpr auto kNetSearch = 90s;
constexpr auto kIpAttach = 30s;
constexpr auto kTcpConnect = 20s;
constexpr auto kAuth = 10s;
constexpr auto kSendTimeout = 20s;
constexpr auto kPingResponse = 10s;
constexpr auto kResetPulse = 300ms;
constexpr auto kResetWait = 5s;
constexpr auto kPowerDown = 4s; /* розряд ємностей фільтрації */
constexpr auto kCloseWait = 3s;
constexpr auto kSimBusy = 1s;
constexpr auto kFatalSleep = 1h;
constexpr auto kNetPoll = 3s;

constexpr unsigned kMaxRetries = 5;
constexpr unsigned kAtProbeLimit = 5;
constexpr auto kBackoffBase = 2000ms;
constexpr auto kBackoffCeiling = 300000ms;

constexpr std::uint8_t kEventTimeout = 0xFF; /* мітка таймауту в чорній скриньці */

constexpr std::array<std::string_view, 3> kInitSequence{
    "ATE0",       /* луна засмічує приймальний буфер */
    "AT+CMEE=2",  /* розширені коди помилок */
    "AT+IFC=2,2"  /* апаратний контроль потоку RTS/CTS */
};

constexpr std::array<std::string_view, 3> kAttachSequence{
    "AT+CGDCONT=1,\"IP\",\"iot.provider.apn\"",
    "AT+CGATT=1",
    "AT+CGPADDR=1"
};

/* Коди CME → сходинка драбини (таблиця зі статті). 0 — пауза без зміни стану. */
unsigned cmeLevel(std::uint16_t code)
{
    switch (code) {
    case 10:  return 5; /* SIM not inserted — лікувати нічим */
    case 13:  return 4; /* SIM failure */
    case 14:  return 0; /* SIM busy: читає адресну книгу */
    case 30:  return 3; /* No network service */
    case 33:  return 2; /* Operation not allowed — немає PDP */
    case 100: return 4; /* фатальний збій бейсбенду */
    default:  return 1;
    }
}

} // namespace

ConnectionFsm::ConnectionFsm(ModemHal& hal, AtLink& link, BlackBox& log)
    : m_hal(hal), m_link(link), m_log(log)
{
    static_assert(kApn == "iot.provider.apn", "APN у команді CGDCONT мусить збігатися");
    m_hal.powerSet(false);
    m_hal.pwrkeySet(false);
    m_hal.resetSet(false);
}

void ConnectionFsm::armTimer(std::chrono::milliseconds timeout)
{
    m_deadline = (timeout > 0ms) ? std::optional{m_hal.now() + timeout} : std::nullopt;
}

void ConnectionFsm::armPoll(std::chrono::milliseconds period)
{
    m_pollPeriod = period;
    m_pollLast = m_hal.now();
}

/* Кадр у сокет: спершу AT+CIPSEND=<len>, тіло — після запрошення '>'. */
void ConnectionFsm::txFrame(std::expected<mqtt::Frame, mqtt::Error> frame)
{
    if (!frame) {
        /* Буфер розрахований на найбільший кадр; якщо не вліз — не шлемо нічого
           й даємо стану вилетіти в драбину відновлення за таймаутом. */
        m_pending = {};
        return;
    }
    m_pending = *frame;

    std::array<char, 24> cmd{};
    constexpr std::string_view prefix = "AT+CIPSEND=";
    std::ranges::copy(prefix, cmd.begin());
    const auto [ptr, ec] = std::to_chars(cmd.data() + prefix.size(), cmd.data() + cmd.size(),
                                         m_pending.size());
    if (ec != std::errc{}) {
        m_pending = {};
        return;
    }
    m_link.sendLine(std::string_view{cmd.data(), static_cast<std::size_t>(ptr - cmd.data())});
}

void ConnectionFsm::enter(State next, std::chrono::milliseconds timeout)
{
    m_log.record(std::to_underlying(m_state), std::to_underlying(next), m_lastEvent,
                 static_cast<std::uint8_t>(m_retry), m_rssiDbm, m_lastCme, m_hal.vbatMv());

    m_state = next;
    m_substep = 0;
    m_pollPeriod = 0ms;
    m_pending = {};
    armTimer(timeout);

    switch (next) {
    case State::NoPower:
        m_hal.powerSet(false);
        m_hal.pwrkeySet(false);
        m_hal.resetSet(false);
        m_log.flush(); /* журнал мусить пережити знеструмлення */
        break;

    case State::PoweringOn:
        m_hal.powerSet(true);
        armTimer(kVbatSettle); /* далі витримки веде substep */
        break;

    case State::ModemReady:
        m_probes = 0;
        m_link.sendLine("AT"); /* автопідлаштування бодрейту */
        armTimer(kAtProbe);
        break;

    case State::SimReady:
        m_link.sendLine("AT+CPIN?");
        armTimer(kSimTimeout);
        break;

    case State::NetSearch:
        m_link.sendLine("AT+CEREG=1"); /* URC про зміну реєстрації */
        m_link.sendLine("AT+CEREG?");
        armPoll(kNetPoll);
        armTimer(kNetSearch);
        break;

    case State::IpAttach:
        m_link.sendLine(kAttachSequence[0]);
        armTimer(kIpAttach);
        break;

    case State::TcpConnect:
        m_link.sendLine("AT+CIPSTART=\"TCP\",\"cloud.example.com\",1883");
        armTimer(kTcpConnect);
        break;

    case State::ProtocolAuth:
        m_mqtt.reset();
        txFrame(mqtt::connect(m_out, kClientId, kUser, kPassword, kKeepAlive));
        armTimer(kAuth);
        break;

    case State::ReadyToSend:
        /* Тракт цілий: драбина відновлення повертається на нульову сходинку. */
        m_level = 0;
        m_retry = 0;
        m_pingPending = false;
        armPoll(std::chrono::duration_cast<std::chrono::milliseconds>(kKeepAlive));
        armTimer(0ms);
        break;

    case State::Sending:
        if (++m_packetId == 0) {
            m_packetId = 1; /* нуль як ідентифікатор MQTT заборонений */
        }
        txFrame(mqtt::publishQos1(m_out, kTopic,
                                  std::span<const std::byte>{m_tx.data(), m_txLen}, m_packetId));
        armTimer(kSendTimeout);
        break;

    case State::Disconnecting:
        txFrame(mqtt::disconnect(m_out));
        armTimer(kCloseWait);
        break;

    case State::PsmSleep:
        /* T3412_ext ≈ 1 год, T3324 ≈ 20 с: радіо спить, реєстрацію тримає мережа. */
        m_link.sendLine("AT+CPSMS=1,,,\"00100001\",\"00000101\"");
        armTimer(0ms);
        break;

    case State::Backoff:
        break; /* час паузи вже пораховано викликачем */

    case State::HwReset:
        m_hal.resetSet(true);
        armTimer(kResetPulse);
        break;

    case State::PowerCycle:
        m_hal.powerSet(false);
        m_hal.pwrkeySet(false);
        m_hal.resetSet(false);
        m_log.flush();
        armTimer(kPowerDown);
        break;

    case State::FatalStop:
        m_hal.powerSet(false);
        m_log.flush();
        armTimer(std::chrono::duration_cast<std::chrono::milliseconds>(kFatalSleep));
        break;
    }
}

/* Усічений двійковий експоненційний відкат із ПОВНИМ джиттером. */
void ConnectionFsm::enterBackoff(State target)
{
    const unsigned shift = std::min(m_retry, 7u);
    const auto span = std::min(kBackoffBase * (1u << shift), kBackoffCeiling);
    /* random(0, span): зсув усередині вікна розводить тисячі вузлів у часі. */
    const auto window = static_cast<std::uint64_t>(span.count()) + 1;
    const auto wait = std::chrono::milliseconds{
        static_cast<std::int64_t>(static_cast<std::uint64_t>(m_hal.random()) % window)};

    m_backoffTarget = target;
    enter(State::Backoff, wait);
}

void ConnectionFsm::escalate(unsigned level)
{
    if (level == m_level) {
        if (++m_retry > kMaxRetries) {
            /* Сходинка вичерпана: штурмувати її далі — марно палити батарею. */
            m_retry = 1;
            ++level;
        }
    } else {
        m_retry = 1;
    }
    m_level = level;

    switch (level) {
    case 1: /* Сокет: модем живий, реєстрація й IP на місці */
        m_link.sendLine("AT+CIPCLOSE");
        enterBackoff(State::TcpConnect);
        break;

    case 2: /* PDP-контекст: радіолінк цілий, IP втрачено */
        m_link.sendLine("AT+CIPCLOSE");
        m_link.sendLine("AT+CGACT=0,1");
        enterBackoff(State::IpAttach);
        break;

    case 3: /* Радіо: перезапуск радіотракту без знеструмлення */
        m_link.sendLine("AT+CIPCLOSE");
        m_link.sendLine("AT+CFUN=0");
        m_link.sendLine("AT+CFUN=1");
        enterBackoff(State::NetSearch);
        break;

    case 4: /* Залізо: спершу RESET, і лише потім силовий ключ */
        enter(State::HwReset);
        break;

    default:
        enter(State::FatalStop);
        break;
    }
}

/* Обмін у межах відкритої сесії: запрошення, SEND OK і байти від брокера. */
void ConnectionFsm::onSessionMessage(const AtMessage& msg)
{
    switch (msg.kind) {
    case MsgKind::Prompt:
        if (!m_pending.empty()) {
            m_link.sendRaw(m_pending);
            m_pending = {};
        }
        return;

    case MsgKind::SendOk:
        /* Модем узяв кадр у свій буфер. Це ще НЕ доставка: підтвердження
           дає лише PUBACK від брокера. */
        return;

    case MsgKind::Error:
        escalate(1);
        return;

    case MsgKind::Data:
        break;

    default:
        return;
    }

    for (const std::byte byte : msg.data) {
        const auto pkt = m_mqtt.feed(byte);
        if (!pkt) {
            continue;
        }
        switch (pkt->kind) {
        case mqtt::Packet::Kind::ConnAck:
            if (m_state != State::ProtocolAuth) {
                break;
            }
            if (pkt->code == 0) {
                m_logPending = m_log.size() > 0;
                enter(State::ReadyToSend);
            } else {
                /* Брокер відмовив у правах — повтори тут не допоможуть. */
                m_lastCme = pkt->code;
                enter(State::FatalStop);
            }
            break;

        case mqtt::Packet::Kind::PubAck:
            if (m_state == State::Sending && pkt->id == m_packetId) {
                if (m_txIsLog) {
                    m_log.markSent(m_txLen);
                    m_logPending = m_log.size() > 0;
                }
                m_txPending = false;
                enter(State::ReadyToSend);
            }
            break;

        case mqtt::Packet::Kind::PingResp:
            m_pingPending = false;
            if (m_state == State::ReadyToSend) {
                armTimer(0ms);
            }
            break;

        case mqtt::Packet::Kind::Broken:
            escalate(1); /* потік зіпсовано — перевідкриваємо сокет */
            return;

        default:
            break;
        }
    }
}

void ConnectionFsm::onMessage(const AtMessage& msg)
{
    m_lastEvent = std::to_underlying(msg.kind);

    /* Спершу — асинхронні сповіщення, що б'ють по тракту незалежно від стану. */
    switch (msg.kind) {
    case MsgKind::Csq:
        m_rssiDbm = static_cast<std::int8_t>(msg.value);
        return;

    case MsgKind::Boot:
        if (m_state > State::PoweringOn) {
            /* Модем перезавантажився САМ: просів VBAT на передавальному
               імпульсі. Усе, що ми про нього знали, більше не чинне. */
            m_lastCme = 0;
            enter(State::ModemReady);
        }
        return;

    case MsgKind::Closed:
        if (m_state >= State::TcpConnect && m_state <= State::Sending) {
            escalate(1);
        } else if (m_state == State::Disconnecting) {
            enter(kPsmEnabled ? State::PsmSleep : State::NoPower);
        }
        return;

    case MsgKind::PdpDeact:
        if (m_state >= State::TcpConnect && m_state <= State::Sending) {
            escalate(2);
        }
        return;

    case MsgKind::CmeError: {
        m_lastCme = static_cast<std::uint16_t>(msg.value);
        const unsigned level = cmeLevel(m_lastCme);
        if (level == 0) { /* SIM busy: пауза й той самий крок */
            m_backoffTarget = m_state;
            enter(State::Backoff, kSimBusy);
        } else {
            escalate(level);
        }
        return;
    }

    case MsgKind::Creg:
        if (msg.value == 1 || msg.value == 5) { /* домашня мережа або роумінг */
            if (m_state == State::NetSearch) {
                m_level = 0;
                m_retry = 0;
                enter(State::IpAttach);
            }
        } else if (m_state > State::NetSearch) {
            escalate(3); /* вишку втрачено */
        }
        return;

    default:
        break;
    }

    switch (m_state) {
    case State::ModemReady:
        if (msg.kind == MsgKind::Ok) {
            if (m_substep < kInitSequence.size()) {
                m_link.sendLine(kInitSequence[m_substep++]);
                armTimer(kAtCommand);
            } else {
                enter(State::SimReady);
            }
        }
        break;

    case State::SimReady:
        if (msg.kind == MsgKind::Cpin) {
            switch (static_cast<SimState>(msg.value)) {
            case SimState::Ready:
                m_substep = 1; /* лишилося дочекатися OK */
                break;
            case SimState::NeedPin:
                m_link.sendLine("AT+CPIN=\"0000\"");
                m_substep = 2;
                armTimer(kSimTimeout);
                break;
            case SimState::Absent:
                /* Картки немає або збій контактів — зв'язку не буде. */
                enter(State::FatalStop);
                break;
            }
        } else if (msg.kind == MsgKind::Ok) {
            if (m_substep == 1) {
                enter(State::NetSearch);
            } else if (m_substep == 2) {
                m_link.sendLine("AT+CPIN?"); /* перевіряємо після введення PIN */
                m_substep = 0;
                armTimer(kSimTimeout);
            }
        } else if (msg.kind == MsgKind::Error) {
            escalate(4);
        }
        break;

    case State::NetSearch:
        break; /* реєстрацію ловить обробник +CREG/+CEREG вище */

    case State::IpAttach:
        if (msg.kind == MsgKind::Ok) {
            if (++m_substep < kAttachSequence.size()) {
                m_link.sendLine(kAttachSequence[m_substep]);
            }
            /* Після останньої команди чекаємо на +CGPADDR з адресою. */
        } else if (msg.kind == MsgKind::IpReady) {
            m_level = 0;
            m_retry = 0;
            enter(State::TcpConnect);
        } else if (msg.kind == MsgKind::Error) {
            escalate(2);
        }
        break;

    case State::TcpConnect:
        if (msg.kind == MsgKind::ConnectOk) {
            m_level = 0;
            m_retry = 0;
            enter(State::ProtocolAuth);
        } else if (msg.kind == MsgKind::Error) {
            escalate(1);
        }
        break;

    case State::ProtocolAuth:
    case State::ReadyToSend:
    case State::Sending:
    case State::Disconnecting:
        onSessionMessage(msg);
        break;

    default:
        break;
    }
}

void ConnectionFsm::onTimeout()
{
    m_lastEvent = kEventTimeout;

    switch (m_state) {
    case State::PoweringOn:
        if (m_substep == 0) { /* напруга усталилася — тиснемо PWRKEY */
            m_hal.pwrkeySet(true);
            m_substep = 1;
            armTimer(kPwrkeyPulse);
        } else if (m_substep == 1) { /* відпускаємо й чекаємо на STATUS */
            m_hal.pwrkeySet(false);
            m_substep = 2;
            armTimer(kStatusWait);
        } else {
            escalate(4); /* пін STATUS не піднявся */
        }
        break;

    case State::ModemReady:
        if (m_substep == 0 && ++m_probes < kAtProbeLimit) {
            m_link.sendLine("AT");
            armTimer(kAtProbe);
        } else {
            escalate(4); /* UART мовчить — це вже залізо */
        }
        break;

    case State::SimReady:
        escalate(4);
        break;

    case State::NetSearch:
        escalate(3);
        break;

    case State::IpAttach:
        escalate(2);
        break;

    case State::TcpConnect:
    case State::ProtocolAuth:
    case State::Sending:
        escalate(1);
        break;

    case State::ReadyToSend:
        /* Мовчання на PINGREQ — класична ознака напіввідкритого сокета:
           локально він «відкритий», але жоден байт не доходить. */
        escalate(1);
        break;

    case State::Disconnecting:
        enter(kPsmEnabled ? State::PsmSleep : State::NoPower);
        break;

    case State::Backoff:
        enter(m_backoffTarget);
        break;

    case State::HwReset:
        if (m_substep == 0) {
            m_hal.resetSet(false);
            m_substep = 1;
            armTimer(kResetWait); /* чекаємо на RDY */
        } else {
            enter(State::PowerCycle); /* скидання не допомогло */
        }
        break;

    case State::PowerCycle:
        enter(State::PoweringOn);
        break;

    case State::FatalStop:
        m_level = 0;
        m_retry = 0;
        enter(State::NoPower);
        break;

    default:
        armTimer(0ms);
        break;
    }
}

void ConnectionFsm::tick()
{
    while (const auto msg = m_link.poll()) {
        onMessage(*msg);
    }

    const auto now = m_hal.now();

    if (m_pollPeriod > 0ms && now - m_pollLast >= m_pollPeriod) {
        m_pollLast = now;
        if (m_state == State::NetSearch) {
            m_link.sendLine("AT+CEREG?");
            m_link.sendLine("AT+CSQ");
        } else if (m_state == State::ReadyToSend && !m_pingPending) {
            /* Keep-alive тримає відкритою трансляцію адрес у мережі оператора. */
            txFrame(mqtt::pingReq(m_out));
            m_pingPending = true;
            armTimer(kPingResponse);
        }
    }

    /* Пін STATUS замість сліпого очікування фіксованої паузи. */
    if (m_state == State::PoweringOn && m_substep == 2 && m_hal.statusPin()) {
        enter(State::ModemReady);
    }

    if (m_state == State::ReadyToSend && !m_pingPending) {
        if (!m_txPending && m_logPending) {
            /* Сесія жива — віддаємо чорну скриньку минулих аварій. */
            const auto frame = m_log.exportFrame(m_tx);
            if (!frame.empty()) {
                m_txLen = frame.size();
                m_txPending = true;
                m_txIsLog = true;
            } else {
                m_logPending = false;
            }
        }
        if (m_txPending) {
            enter(State::Sending);
        } else if (m_wantDisconnect) {
            m_wantDisconnect = false;
            enter(State::Disconnecting);
        }
    }

    if (m_deadline && m_hal.now() >= *m_deadline) {
        onTimeout();
    }
}

void ConnectionFsm::connect()
{
    if (m_state == State::NoPower) {
        enter(State::PoweringOn);
    } else if (m_state == State::PsmSleep) {
        /* Реєстрацію та IP мережа тримала за нас: одразу відкриваємо сокет. */
        enter(State::TcpConnect);
    }
}

bool ConnectionFsm::submit(std::span<const std::byte> payload)
{
    if (payload.empty() || payload.size() > kPayloadMax) {
        return false; /* краще відмовити явно, ніж мовчки різати кадр */
    }
    if (m_txPending) {
        return false; /* один кадр у польоті: черги під телеметрію тут немає */
    }
    std::ranges::copy(payload, m_tx.begin());
    m_txLen = payload.size();
    m_txPending = true;
    m_txIsLog = false;
    connect();
    return true;
}

void ConnectionFsm::disconnect()
{
    m_wantDisconnect = true;
}
