#include "service_engine.hpp"

#include <algorithm>
#include <charconv>
#include <cstddef>

#include "self_test.hpp"

namespace {

// Спільний секрет. У виробі його читають з OTP чи захищеної сторінки flash.
constexpr std::string_view kSecret = "SRV-2026-PLANT-KEY";

constexpr std::uint16_t kAdcVrefMilliVolts = 3300;
constexpr std::uint16_t kAdcFullScale      = 4096;
constexpr std::int32_t  kCalLimitMilliVolts = 500;

constexpr std::string_view ltrim(std::string_view s) noexcept
{
    while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) {
        s.remove_prefix(1);
    }
    return s;
}

// Число з голови рядка. std::from_chars не алокує й не тягне локаль —
// на відміну від sscanf, який у прошивці коштує кілька кілобайтів коду.
template <class T>
std::optional<T> takeNumber(std::string_view& args) noexcept
{
    args = ltrim(args);
    T value{};
    const auto* first  = args.data();
    const auto* last   = args.data() + args.size();
    const auto  result = std::from_chars(first, last, value);
    if (result.ec != std::errc{}) {
        return std::nullopt;
    }
    args.remove_prefix(static_cast<std::size_t>(result.ptr - first));
    return value;
}

std::uint32_t fnv1a(std::span<const std::byte> data, std::uint32_t hash) noexcept
{
    for (auto byte : data) {
        hash ^= std::to_integer<std::uint32_t>(byte);
        hash *= 16777619u;
    }
    return hash;
}

// Очікувана відповідь на виклик. FNV-1a — НЕ криптографія: він показує форму
// обміну (nonce + секрет -> відповідь), а у виробі тут стоїть HMAC-SHA256.
std::array<char, 8> expectedResponse(std::uint32_t nonce) noexcept
{
    std::uint32_t hash = fnv1a(std::as_bytes(std::span{kSecret.data(), kSecret.size()}), 2166136261u);
    hash = fnv1a(std::as_bytes(std::span{&nonce, 1}), hash);

    std::array<char, 8> out{};
    std::format_to_n(out.data(), out.size(), "{:08X}", hash);
    return out;
}

// Порівняння без ранньої відсічі: час відповіді не має підказувати,
// скільки символів ключа вгадано.
bool constantTimeEqual(std::string_view a, std::string_view b) noexcept
{
    if (a.size() != b.size()) {
        return false;
    }
    unsigned char diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<unsigned char>(a[i] ^ b[i]);
    }
    return diff == 0;
}

constexpr std::string_view describe(ServiceEngine::Error error) noexcept
{
    using E = ServiceEngine::Error;
    switch (error) {
    case E::Locked:            return "LOCKED_ENTER_AUTH_FIRST";
    case E::AccessDenied:      return "ACCESS_DENIED";
    case E::InvalidChannel:    return "INVALID_CHANNEL";
    case E::TimeoutOutOfRange: return "VALUE_OUT_OF_RANGE";
    case E::AuthFailed:        return "AUTH_FAILED";
    case E::BadArguments:      return "BAD_ARGUMENTS";
    case E::UnknownCommand:    return "UNKNOWN_COMMAND";
    case E::ActuationBusy:     return "ACTUATION_ACTIVE_USE_ACT_OFF";
    case E::LineTooLong:       return "LINE_TOO_LONG";
    case E::HardwareFault:     return "EMERGENCY_POWER_CYCLE_REQUIRED";
    case E::EepromWriteFailed: return "EEPROM_WRITE_FAILED";
    case E::BusBusy:           return "I2C_BUS_BUSY";
    case E::InputOverrun:      return "INPUT_OVERRUN_LINE_DROPPED";
    }
    return "UNKNOWN";
}

constexpr std::string_view stateName(ServiceEngine::State state) noexcept
{
    using S = ServiceEngine::State;
    switch (state) {
    case S::Locked:          return "LOCKED";
    case S::ChallengeIssued: return "CHALLENGE";
    case S::Unlocked:        return "UNLOCKED";
    case S::ActuationActive: return "ACTUATION";
    case S::Emergency:       return "EMERGENCY";
    }
    return "?";
}

} // namespace

const std::array<ServiceEngine::Command, 10> ServiceEngine::kCommands{{
    // назва             обробник                            сесія  під напругою  в аварії
    {"sys info",        &ServiceEngine::cmdSysInfo,        false, true,  true},
    {"auth challenge",  &ServiceEngine::cmdAuthChallenge,  false, false, false},
    {"auth key",        &ServiceEngine::cmdAuthKey,        false, false, false},
    {"sys lock",        &ServiceEngine::cmdLock,           true,  true,  false},
    {"diag act off",    &ServiceEngine::cmdActuateOff,     true,  true,  false},
    {"diag act relay",  &ServiceEngine::cmdActuateRelay,   true,  false, false},
    {"diag selftest",   &ServiceEngine::cmdSelfTest,       true,  false, false},
    {"diag adc",        &ServiceEngine::cmdAdc,            true,  false, false},
    {"cal get",         &ServiceEngine::cmdCalGet,         true,  false, false},
    {"cal set",         &ServiceEngine::cmdCalSet,         true,  false, false},
}};

// ---- Actuation ------------------------------------------------------------

ServiceEngine::Actuation::Actuation(std::uint8_t channel, hw::Millis deadline) noexcept
    : channel_(channel), deadline_(deadline)
{
    // Дедлайн зафіксовано ДО подачі напруги: інакше скидання між двома
    // рядками лишило б реле ввімкненим без жодного відліку.
    hw::setRelay(channel_, true);
}

ServiceEngine::Actuation::Actuation(Actuation&& other) noexcept
    : channel_(other.channel_), deadline_(other.deadline_)
{
    other.channel_ = 0; // джерело більше нічим не володіє
}

ServiceEngine::Actuation::~Actuation()
{
    if (channel_ != 0) {
        hw::setRelay(channel_, false);
    }
}

// ---- службове -------------------------------------------------------------

void ServiceEngine::emit(std::string_view text) noexcept
{
    hw::uartWrite(text);
}

void ServiceEngine::prompt() noexcept
{
    if (state_ == State::Unlocked || state_ == State::ActuationActive) {
        emit("SRV> ");
    }
}

void ServiceEngine::refreshSession() noexcept
{
    if (state_ == State::Unlocked || state_ == State::ActuationActive) {
        stateDeadline_ = hw::now() + SessionTimeout;
    }
}

void ServiceEngine::enterLocked() noexcept
{
    emergencyAllOff();
    state_ = State::Locked;
    nonce_ = 0;
}

void ServiceEngine::report(Result result) noexcept
{
    if (result) {
        errorCount_ = 0;
        refreshSession(); // кожна валідна команда поновлює відлік
        return;
    }
    emitf("-ERR: 0x{:04X} {}\r\n", static_cast<std::uint16_t>(result.error()),
          describe(result.error()));

    // Лічильник помилок переповнився: або лінія шумить, або хтось перебирає
    // команди наосліп. Знеструмлюємо й вимагаємо нової автентифікації.
    if (++errorCount_ >= MaxErrors) {
        enterLocked();
        errorCount_ = 0;
        emit("[EVENT: ERROR_LIMIT_LOCKED]\r\n");
    }
}

// ---- команди --------------------------------------------------------------

ServiceEngine::Result ServiceEngine::cmdSysInfo(std::string_view args)
{
    if (!ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    emitf("+OK: STATE={} UPTIME={}s FAULTS=0x{:04X} ERRORS={}\r\n",
          stateName(state_),
          hw::now().count() / 1000,
          static_cast<std::uint32_t>(faults_),
          errorCount_);
    return {};
}

ServiceEngine::Result ServiceEngine::cmdAuthChallenge(std::string_view args)
{
    if (!ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    if (state_ == State::Unlocked || state_ == State::ActuationActive) {
        return std::unexpected(Error::AccessDenied);
    }
    nonce_         = hw::random();
    state_         = State::ChallengeIssued;
    stateDeadline_ = hw::now() + ChallengeTimeout;
    emitf("+OK: CHALLENGE {:08X} (ANSWER WITHIN 30 S)\r\n", nonce_);
    return {};
}

ServiceEngine::Result ServiceEngine::cmdAuthKey(std::string_view args)
{
    if (state_ != State::ChallengeIssued) {
        return std::unexpected(Error::AuthFailed);
    }
    const auto key      = ltrim(args);
    const auto expected = expectedResponse(nonce_);
    if (!constantTimeEqual(key, std::string_view(expected.data(), expected.size()))) {
        enterLocked(); // одна хиба — і виклик згорає
        return std::unexpected(Error::AuthFailed);
    }
    state_         = State::Unlocked;
    stateDeadline_ = hw::now() + SessionTimeout;
    nonce_         = 0; // одноразовий: повтор того самого рядка не пройде
    emit("+OK: SERVICE_UNLOCKED (SESSION 15 MIN)\r\n");
    return {};
}

ServiceEngine::Result ServiceEngine::cmdLock(std::string_view args)
{
    if (!ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    enterLocked();
    emit("+OK: SERVICE_LOCKED\r\n");
    return {};
}

ServiceEngine::Result ServiceEngine::cmdActuateOff(std::string_view args)
{
    if (!ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    emergencyAllOff();
    emit("+OK: ALL_OUTPUTS_OFF\r\n");
    return {};
}

ServiceEngine::Result ServiceEngine::cmdActuateRelay(std::string_view args)
{
    const auto channel = takeNumber<std::uint32_t>(args);
    const auto seconds = takeNumber<std::uint32_t>(args);
    if (!channel || !seconds || !ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    if (*channel < 1 || *channel > hw::RelayCount) {
        return std::unexpected(Error::InvalidChannel);
    }
    if (*seconds == 0 || std::chrono::seconds(*seconds) > MaxActuation) {
        return std::unexpected(Error::TimeoutOutOfRange);
    }
    if (any(faults_)) {
        return std::unexpected(Error::HardwareFault);
    }

    emergencyAllOff(); // два канали одночасно не вмикаємо
    actuation_.emplace(static_cast<std::uint8_t>(*channel),
                       hw::now() + std::chrono::seconds(*seconds));
    state_ = State::ActuationActive;
    emitf("+OK: RELAY_{} ACTIVE FOR {} SEC\r\n", *channel, *seconds);
    return {};
}

ServiceEngine::Result ServiceEngine::cmdSelfTest(std::string_view args)
{
    if (!ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    const auto report = diag::runBist();
    if (!report) {
        return std::unexpected(report.error() == diag::BusError::Busy ? Error::BusBusy
                                                                      : Error::HardwareFault);
    }
    emitf("+OK: BIST (BUS:{}, RTC:{}, EEPROM:{}, ADC0_RAW:0x{:04X}, ADC0_MV:{})\r\n",
          report->busFree ? "FREE" : "STUCK",
          report->rtcOk ? "OK" : "FAULT",
          report->eepromOk ? "OK" : "FAULT",
          report->adcRaw,
          report->adcMilliVolts);
    return {};
}

ServiceEngine::Result ServiceEngine::cmdAdc(std::string_view args)
{
    const auto channel = takeNumber<std::uint32_t>(args);
    if (!channel || !ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    if (*channel > 7) {
        return std::unexpected(Error::InvalidChannel);
    }
    const auto raw = hw::adcRaw(static_cast<std::uint8_t>(*channel));
    auto millivolts = static_cast<std::int32_t>(std::uint32_t{raw} * kAdcVrefMilliVolts / kAdcFullScale);
    if (*channel < CalSlots) {
        millivolts += cal_[*channel]; // зсув нуля з калібрування
    }
    emitf("+OK: ADC{} RAW=0x{:04X} MV={}\r\n", *channel, raw, millivolts);
    return {};
}

ServiceEngine::Result ServiceEngine::cmdCalGet(std::string_view args)
{
    if (!ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    emitf("+OK: CAL 0={}MV 1={}MV 2={}MV 3={}MV\r\n", cal_[0], cal_[1], cal_[2], cal_[3]);
    return {};
}

ServiceEngine::Result ServiceEngine::cmdCalSet(std::string_view args)
{
    const auto slot  = takeNumber<std::uint32_t>(args);
    const auto value = takeNumber<std::int32_t>(args);
    if (!slot || !value || !ltrim(args).empty()) {
        return std::unexpected(Error::BadArguments);
    }
    if (*slot >= CalSlots) {
        return std::unexpected(Error::InvalidChannel);
    }
    if (*value < -kCalLimitMilliVolts || *value > kCalLimitMilliVolts) {
        return std::unexpected(Error::TimeoutOutOfRange);
    }
    cal_[*slot] = *value;
    const auto address = static_cast<std::uint16_t>(CalEepromBase + *slot * sizeof(std::int32_t));
    if (!hw::eepromWrite(address, std::as_bytes(std::span{&cal_[*slot], 1}))) {
        return std::unexpected(Error::EepromWriteFailed);
    }
    emitf("+OK: CAL {}={}MV STORED\r\n", *slot, *value);
    return {};
}

// ---- диспетчер ------------------------------------------------------------

ServiceEngine::Result ServiceEngine::dispatch(std::string_view line) noexcept
{
    const Command*   command = nullptr;
    std::string_view args{};

    for (const auto& entry : kCommands) {
        if (line == entry.name) {
            command = &entry;
            break;
        }
        if (line.starts_with(entry.name) && line.size() > entry.name.size()
            && line[entry.name.size()] == ' ') {
            command = &entry;
            args    = line.substr(entry.name.size() + 1);
            break;
        }
    }
    if (command == nullptr) {
        return std::unexpected(Error::UnknownCommand);
    }
    // В аварії лишається одна команда — подивитися, що саме спрацювало.
    if (state_ == State::Emergency && !command->duringEmergency) {
        return std::unexpected(Error::HardwareFault);
    }
    if (command->needsSession && state_ != State::Unlocked && state_ != State::ActuationActive) {
        return std::unexpected(Error::Locked);
    }
    // Поки навантаження під напругою, приймаємо лише те, що його знімає.
    if (state_ == State::ActuationActive && !command->duringActuation) {
        return std::unexpected(Error::ActuationBusy);
    }
    return (this->*(command->handler))(args);
}

// ---- публічний інтерфейс --------------------------------------------------

void ServiceEngine::begin() noexcept
{
    emergencyAllOff();

    for (std::size_t slot = 0; slot < CalSlots; ++slot) {
        std::int32_t stored = 0;
        const auto   address = static_cast<std::uint16_t>(CalEepromBase + slot * sizeof(std::int32_t));
        if (hw::eepromRead(address, std::as_writable_bytes(std::span{&stored, 1}))
            && stored >= -kCalLimitMilliVolts && stored <= kCalLimitMilliVolts) {
            cal_[slot] = stored; // сміття з чистої EEPROM просто ігноруємо
        }
    }
    emit("\r\n[SERVICE ENGINE READY - 'auth challenge' TO START]\r\n");
}

void ServiceEngine::emergencyAllOff() noexcept
{
    actuation_.reset(); // деструктор гасить свій канал
    // І ще раз, прямо по GPIO: ця функція мусить спрацювати навіть тоді,
    // коли стан об'єкта вже зіпсовано.
    for (std::uint8_t channel = 1; channel <= hw::RelayCount; ++channel) {
        hw::setRelay(channel, false);
    }
    if (state_ == State::ActuationActive) {
        state_ = State::Unlocked;
    }
}

void ServiceEngine::faultTrip(hw::Fault flags) noexcept
{
    // Контекст ISR: гасимо виходи й фіксуємо причину. Друкувати звідси не
    // можна — повідомлення видасть poll() у своєму контексті.
    for (std::uint8_t channel = 1; channel <= hw::RelayCount; ++channel) {
        hw::setRelay(channel, false);
    }
    actuation_.reset();
    faults_             |= flags;
    state_               = State::Emergency;
    emergencyAnnounced_  = false;
}

void ServiceEngine::feedByte(char c) noexcept
{
    if (c == '\r' || c == '\n') {
        if (rxIdx_ == 0 && !rxOverflow_) {
            return; // порожній рядок — просто Enter
        }
        if (lineReady_.load(std::memory_order_acquire)) {
            // Задача ще не забрала попередній рядок: новий втрачаємо
            // свідомо, бо переписувати буфер під нею не можна.
            lineLost_.store(true, std::memory_order_release);
        } else {
            std::copy_n(rx_.begin(), rxIdx_, line_.begin());
            lineLen_      = rxIdx_;
            lineOverflow_ = rxOverflow_;
            lineReady_.store(true, std::memory_order_release);
        }
        rxIdx_      = 0;
        rxOverflow_ = false;
        return;
    }

    if (c < 0x20 || c > 0x7E) {
        return; // керуючі символи й брязкіт лінії відкидаємо
    }
    if (rxIdx_ + 1 < rx_.size()) {
        rx_[rxIdx_++] = c;
    } else {
        rxOverflow_ = true; // індекс став на 127 і далі не рухається
    }
}

void ServiceEngine::poll() noexcept
{
    const auto now = hw::now();

    if (const auto faults = hw::faultFlags(); any(faults) && state_ != State::Emergency) {
        faultTrip(faults);
    }
    if (state_ == State::Emergency && !emergencyAnnounced_) {
        emitf("\r\n[EVENT: EMERGENCY_STOP FLAGS=0x{:04X} - POWER CYCLE REQUIRED]\r\n",
              static_cast<std::uint32_t>(faults_));
        emergencyAnnounced_ = true;
    }

    if (actuation_ && now >= actuation_->deadline()) {
        emergencyAllOff(); // повертає автомат в Unlocked
        emit("\r\n[EVENT: ACTUATION_TIMEOUT_AUTO_SHUTDOWN]\r\n");
        prompt();
    }
    if (state_ == State::ChallengeIssued && now >= stateDeadline_) {
        enterLocked();
        emit("\r\n[EVENT: CHALLENGE_EXPIRED_LOCKED]\r\n");
    }
    if ((state_ == State::Unlocked || state_ == State::ActuationActive) && now >= stateDeadline_) {
        enterLocked();
        emit("\r\n[EVENT: SESSION_TIMEOUT_LOCKED]\r\n");
    }

    if (lineLost_.exchange(false, std::memory_order_acquire)) {
        report(std::unexpected(Error::InputOverrun));
    }
    if (!lineReady_.load(std::memory_order_acquire)) {
        return;
    }
    if (lineOverflow_) {
        lineOverflow_ = false;
        report(std::unexpected(Error::LineTooLong));
    } else {
        report(dispatch(std::string_view(line_.data(), lineLen_)));
    }
    // Прапорець знімаємо ПІСЛЯ розбору: доти ISR не має права чіпати line_.
    lineReady_.store(false, std::memory_order_release);
    prompt();
}
