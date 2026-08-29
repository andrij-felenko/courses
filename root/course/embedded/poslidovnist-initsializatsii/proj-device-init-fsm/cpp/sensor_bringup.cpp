#include "sensor_bringup.hpp"

namespace bringup {

std::string_view to_string(State state) noexcept
{
    switch (state) {
        case State::PowerOnDelay:   return "PowerOnDelay";
        case State::SendReset:      return "SendReset";
        case State::PollReady:      return "PollReady";
        case State::VerifyChipId:   return "VerifyChipId";
        case State::WriteConfig:    return "WriteConfig";
        case State::ReadbackVerify: return "ReadbackVerify";
        case State::Activate:       return "Activate";
        case State::SettlingDelay:  return "SettlingDelay";
        case State::Ready:          return "Ready";
        case State::RetryBackoff:   return "RetryBackoff";
        case State::FaultSafe:      return "FaultSafe";
    }
    return "?";
}

SensorBringUp::SensorBringUp(I2cBus& bus, Millis now,
                             std::span<const RegConfig> config) noexcept
    : bus_(bus), config_(config), entered_(now)
{
}

void SensorBringUp::enter(State state, Millis now) noexcept
{
    state_ = state;
    entered_ = now;
}

bool SensorBringUp::elapsed(Millis now, Millis span) const noexcept
{
    return now - entered_ >= span;
}

void SensorBringUp::retry_or_fail(std::string_view reason, Millis now)
{
    ++retries_;

    if (retries_ <= kMaxRetries) {
        // Ведений міг зупинитися посеред байта й затиснути SDA в нулі —
        // без дев'яти тактів SCL наступний START не сформується.
        bus_.recover();
        backoff_ = kBaseBackoff * (1U << (retries_ - 1U));  // 50, 100, 200 мс
        enter(State::RetryBackoff, now);
    } else {
        fault_ = reason;
        enter(State::FaultSafe, now);
    }
}

void SensorBringUp::step(Millis now)
{
    switch (state_) {

        case State::PowerOnDelay:
            // Доки V_DD наростає й піднімається внутрішній LDO, чип німий.
            if (elapsed(now, kPorBoot)) {
                enter(State::SendReset, now);
            }
            break;

        case State::SendReset:
            if (bus_.write(reg::Address, reg::ResetCtrl, bit::SwReset)) {
                enter(State::PollReady, now);
            } else {
                retry_or_fail("NACK на команді SW_RESET", now);
            }
            break;

        case State::PollReady: {
            // Перші мілісекунди після скидання цифрове ядро вимкнене й
            // відповідає NACK. Без цієї паузи драйвер спалив би ліміт спроб
            // на власному ж скиданні.
            if (!elapsed(now, kResetWait)) {
                break;
            }
            const ReadResult status = bus_.read(reg::Address, reg::ResetCtrl);
            if (status && (*status & bit::SwReset) == 0 &&
                (*status & bit::DeviceReady) != 0) {
                enter(State::VerifyChipId, now);
                break;
            }
            if (elapsed(now, kPollTimeout)) {
                retry_or_fail("таймаут очікування біта готовності", now);
            }
            break;
        }

        case State::VerifyChipId: {
            const ReadResult id = bus_.read(reg::Address, reg::ChipId);
            if (!id) {
                retry_or_fail("помилка шини при читанні WHO_AM_I", now);
            } else if (*id != kExpectedChipId) {
                // На брудній шині це частіше збитий байт, ніж справді інший
                // чип; стабільна розбіжність доведе автомат до FaultSafe.
                retry_or_fail("невірний WHO_AM_I", now);
            } else {
                config_idx_ = 0;
                enter(State::WriteConfig, now);
            }
            break;
        }

        case State::WriteConfig: {
            if (config_idx_ >= config_.size()) {
                enter(State::Activate, now);
                break;
            }
            const RegConfig& entry = config_[config_idx_];
            if (bus_.write(reg::Address, entry.reg, entry.value)) {
                enter(State::ReadbackVerify, now);
            } else {
                retry_or_fail("помилка запису конфігурації", now);
            }
            break;
        }

        case State::ReadbackVerify: {
            const RegConfig& entry = config_[config_idx_];
            const ReadResult actual = bus_.read(reg::Address, entry.reg);
            if (!actual) {
                retry_or_fail("помилка шини при Read-Back", now);
            } else if ((*actual & entry.mask) != (entry.value & entry.mask)) {
                // Порівнюємо лише за маскою: статусні біти живуть своїм життям.
                retry_or_fail("розбіжність Read-Back", now);
            } else {
                ++config_idx_;
                enter(State::WriteConfig, now);
            }
            break;
        }

        case State::Activate:
            if (bus_.write(reg::Address, reg::PwrMode, kPwrActive)) {
                enter(State::SettlingDelay, now);
            } else {
                retry_or_fail("помилка переходу в робочий режим", now);
            }
            break;

        case State::SettlingDelay:
            // Перші вибірки після вмикання аналогового тракту недостовірні.
            if (elapsed(now, kAnalogSettle)) {
                retries_ = 0;  // запуск удався — ліміт спроб знову повний
                enter(State::Ready, now);
            }
            break;

        case State::RetryBackoff:
            if (elapsed(now, backoff_)) {
                // Починаємо з нуля: чип міг перезавантажитися по живленню.
                config_idx_ = 0;
                enter(State::PowerOnDelay, now);
            }
            break;

        case State::Ready:
        case State::FaultSafe:
            // Кінцеві стани: штатна робота або зафіксована аварія.
            break;
    }
}

}  // namespace bringup
