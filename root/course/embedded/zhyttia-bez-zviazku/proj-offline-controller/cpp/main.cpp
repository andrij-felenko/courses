/* =========================================================================
 * C++20/C++23 Ідіоматична реалізація автономного контролера
 * ========================================================================= */
#include <array>
#include <span>
#include <cstdint>
#include <optional>
#include <chrono>
#include <algorithm>
#include <concepts>
#include <expected>

namespace embedded::edge {

enum class EventPriority : uint8_t {
    Alarm = 0,     // Жорстке збереження без переповнення
    Audit = 1,     // Журнал операцій, кільцевий FIFO
    Telemetry = 2  // Періодичні виміри, витіснення та деградація
};

enum class ReconcileError {
    SafetyConflict,
    StaleVersion,
    StorageFull
};

struct OfflineEvent {
    std::chrono::seconds timestamp{0};
    uint32_t             sequence_id{0};
    uint16_t             event_code{0};
    int16_t              payload_val{0};
    EventPriority        priority{EventPriority::Telemetry};
    bool                 acknowledged{false};
};

template <size_t Capacity, bool AllowOverwrite>
class FixedRingBuffer {
public:
    constexpr FixedRingBuffer() = default;

    [[nodiscard]] bool push(const OfflineEvent& ev) noexcept {
        if (m_count >= Capacity) {
            if constexpr (!AllowOverwrite) {
                m_dropped_count++;
                return false;
            } else {
                m_tail = (m_tail + 1) % Capacity;
                m_count--;
                m_dropped_count++;
            }
        }
        m_storage[m_head] = ev;
        m_head = (m_head + 1) % Capacity;
        m_count++;
        return true;
    }

    [[nodiscard]] std::optional<OfflineEvent> peek() const noexcept {
        if (m_count == 0) return std::nullopt;
        return m_storage[m_tail];
    }

    void pop() noexcept {
        if (m_count > 0) {
            m_tail = (m_tail + 1) % Capacity;
            m_count--;
        }
    }

    [[nodiscard]] size_t size() const noexcept { return m_count; }
    [[nodiscard]] bool empty() const noexcept { return m_count == 0; }
    [[nodiscard]] uint32_t dropped_count() const noexcept { return m_dropped_count; }

private:
    std::array<OfflineEvent, Capacity> m_storage{};
    size_t m_head{0};
    size_t m_tail{0};
    size_t m_count{0};
    uint32_t m_dropped_count{0};
};

struct LocalRules {
    int16_t temp_threshold_c_x10{220};  // 22.0 °C
    int16_t temp_hysteresis_c_x10{15};  // 1.5 °C
    std::chrono::seconds safe_timeout{3600};
    bool heater_forced_off{false};
};

struct DeviceState {
    uint32_t state_version{1};
    uint32_t cloud_known_version{0};
    bool     heater_active{false};
    bool     alarm_latched{false};
    int16_t  last_temperature{0};
};

class SovereignOfflineController {
public:
    static constexpr size_t AlarmQueueCap     = 8;
    static constexpr size_t AuditQueueCap     = 16;
    static constexpr size_t TelemetryQueueCap = 32;

    SovereignOfflineController() = default;

    // Циклічна обробка фізичного процесу
    void process_control_loop(int16_t current_temp_x10,
                              std::chrono::seconds rtc_now,
                              std::chrono::milliseconds dt) noexcept {
        m_state.last_temperature = current_temp_x10;

        if (!m_network_online) {
            m_offline_duration += std::chrono::duration_cast<std::chrono::seconds>(dt);
        } else {
            m_offline_duration = std::chrono::seconds{0};
        }

        // 1. Перевірка на критичний перегрів
        if (current_temp_x10 > 500 && !m_state.alarm_latched) {
            m_state.alarm_latched = true;
            m_state.heater_active = false;
            m_state.state_version++;

            m_alarms.push(OfflineEvent{
                .timestamp = rtc_now,
                .sequence_id = ++m_global_seq,
                .event_code = 0xE001,
                .payload_val = current_temp_x10,
                .priority = EventPriority::Alarm,
                .acknowledged = false
            });
            return;
        }

        if (m_state.alarm_latched || m_rules.heater_forced_off) {
            m_state.heater_active = false;
            return;
        }

        // 2. Локальний гістерезисний регулятор
        const auto target = m_rules.temp_threshold_c_x10;
        const auto hyst   = m_rules.temp_hysteresis_c_x10;
        const bool prev_heater = m_state.heater_active;

        if (current_temp_x10 < (target - hyst)) {
            m_state.heater_active = true;
        } else if (current_temp_x10 > (target + hyst)) {
            m_state.heater_active = false;
        }

        if (prev_heater != m_state.heater_active) {
            m_state.state_version++;
            m_audits.push(OfflineEvent{
                .timestamp = rtc_now,
                .sequence_id = ++m_global_seq,
                .event_code = 0xA010,
                .payload_val = static_cast<int16_t>(m_state.heater_active),
                .priority = EventPriority::Audit,
                .acknowledged = false
            });
        }
    }

    // Періодична телеметрія з дельта-фільтром
    void log_telemetry(std::chrono::seconds rtc_now, int16_t current_temp_x10) noexcept {
        const int16_t diff = std::abs(current_temp_x10 - m_last_logged_temp);
        if (diff >= 5 || m_last_logged_temp == -9999) {
            m_last_logged_temp = current_temp_x10;
            m_telemetry.push(OfflineEvent{
                .timestamp = rtc_now,
                .sequence_id = ++m_global_seq,
                .event_code = 0x1001,
                .payload_val = current_temp_x10,
                .priority = EventPriority::Telemetry,
                .acknowledged = false
            });
        }
    }

    // Семантична реконсиліація стану при отриманні наказу з бекенду
    [[nodiscard]] std::expected<void, ReconcileError> reconcile_cloud_state(
        uint32_t cloud_version,
        int16_t new_temp_target_x10,
        bool force_heater_off) noexcept {
        
        // Локальна аварія переважає дистанційне керування
        if (m_state.alarm_latched && !force_heater_off) {
            return std::unexpected(ReconcileError::SafetyConflict);
        }

        if (cloud_version <= m_state.cloud_known_version) {
            return std::unexpected(ReconcileError::StaleVersion);
        }

        m_rules.temp_threshold_c_x10 = new_temp_target_x10;
        m_rules.heater_forced_off = force_heater_off;
        m_state.cloud_known_version = cloud_version;
        m_state.state_version = cloud_version + 1;

        return {};
    }

    // Отримання чергової події для вивантаження
    [[nodiscard]] std::optional<OfflineEvent> fetch_next_sync_event() const noexcept {
        if (auto ev = m_alarms.peek()) return ev;
        if (auto ev = m_audits.peek()) return ev;
        if (auto ev = m_telemetry.peek()) return ev;
        return std::nullopt;
    }

    // Підтвердження збереження подією бекендом
    void acknowledge_top_event() noexcept {
        if (!m_alarms.empty()) {
            m_alarms.pop();
        } else if (!m_audits.empty()) {
            m_audits.pop();
        } else if (!m_telemetry.empty()) {
            m_telemetry.pop();
        }
    }

    void set_network_status(bool online) noexcept { m_network_online = online; }
    [[nodiscard]] const DeviceState& state() const noexcept { return m_state; }

private:
    LocalRules   m_rules{};
    DeviceState  m_state{};
    FixedRingBuffer<AlarmQueueCap, false>     m_alarms{};     // Без перезапису
    FixedRingBuffer<AuditQueueCap, true>      m_audits{};     // FIFO з витісненням
    FixedRingBuffer<TelemetryQueueCap, true>  m_telemetry{};  // FIFO з деградацією

    uint32_t             m_global_seq{0};
    int16_t              m_last_logged_temp{-9999};
    std::chrono::seconds m_offline_duration{0};
    bool                 m_network_online{false};
};

} // namespace embedded::edge
