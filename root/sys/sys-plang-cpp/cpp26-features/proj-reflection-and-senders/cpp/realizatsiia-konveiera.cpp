#include <execution>
#include <contracts>
#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <cmath>
#include <expected>

// Структура сирого пакета від апаратних сенсорів
struct RawTelemetryPacket {
    uint32_t packet_id;
    double raw_altitude;
    double raw_velocity;
    double gyro_x;
    double gyro_y;
    double gyro_z;
    bool checksum_valid;
};

// Структура обробленого польотного стану
struct ProcessedFlightState {
    uint32_t packet_id;
    double corrected_altitude;
    double total_angular_velocity;
    std::string flight_status;
};

// Перелік можливих помилок обробки
enum class TelemetryError {
    CorruptedChecksum,
    SensorDataOutOfRange,
    StorageFailure
};

// 1. Етап верифікації даних із мовним контрактом
std::expected<RawTelemetryPacket, TelemetryError> validate_packet(RawTelemetryPacket pkt)
    pre (pkt.packet_id > 0)
{
    if (!pkt.checksum_valid) {
        return std::unexpected(TelemetryError::CorruptedChecksum);
    }
    if (std::isnan(pkt.raw_altitude) || pkt.raw_altitude < -500.0 || pkt.raw_altitude > 50000.0) {
        return std::unexpected(TelemetryError::SensorDataOutOfRange);
    }
    return pkt;
}

// 2. Етап важких математичних обчислень динаміки польоту
ProcessedFlightState compute_flight_dynamics(RawTelemetryPacket pkt) {
    double total_gyro = std::sqrt(pkt.gyro_x * pkt.gyro_x + 
                                  pkt.gyro_y * pkt.gyro_y + 
                                  pkt.gyro_z * pkt.gyro_z);

    // Барометрична корекція висоти за калібрувальною формулою
    double altitude_baro_corrected = pkt.raw_altitude * 1.0024 - 1.2;

    std::string status = "STABLE_CRUISE";
    if (total_gyro > 45.0) {
        status = "HIGH_ANGULAR_ROTATION";
    }

    return ProcessedFlightState{
        .packet_id = pkt.packet_id,
        .corrected_altitude = altitude_baro_corrected,
        .total_angular_velocity = total_gyro,
        .flight_status = status
    };
}

// 3. Асинхронний конвеєр на базі адаптерів P2300
template <std::execution::scheduler IoSched, std::execution::scheduler ComputeSched>
auto make_telemetry_pipeline(RawTelemetryPacket input_packet, 
                            IoSched io_scheduler, 
                            ComputeSched compute_scheduler) 
{
    namespace ex = std::execution;

    // Фаза опису операції: граф будується як композиція легковажних сендерів
    return ex::just(input_packet)
        // 1. Починаємо роботу на I/O-контексті прийому пакетів
        | ex::starts_on(io_scheduler)
        // 2. Виконуємо швидку перевірку цілісності
        | ex::then([](RawTelemetryPacket pkt) {
            return validate_packet(pkt);
        })
        // 3. Розгалуження: якщо дані коректні, переходимо на математичний пул ядер
        | ex::let_value([compute_scheduler](std::expected<RawTelemetryPacket, TelemetryError> val_res) {
            if (!val_res.has_value()) {
                // Відправляємо помилку в асинхронний канал set_error
                return ex::just_error(val_res.error());
            }
            // Переносимо виконання на обчислювальний планувальник
            return ex::just(val_res.value())
                | ex::continues_on(compute_scheduler)
                | ex::then([](RawTelemetryPacket valid_pkt) {
                    return compute_flight_dynamics(valid_pkt);
                });
        })
        // 4. Фіксація результату в консолі або журналі польоту
        | ex::then([](ProcessedFlightState state) {
            std::cout << std::format("[TELEMETRY] Пакет #{:06d}: Висота = {:.2f}м, Обертання = {:.2f}°/с, Стан = {}\n",
                                     state.packet_id, 
                                     state.corrected_altitude, 
                                     state.total_angular_velocity, 
                                     state.flight_status);
            return true;
        })
        // 5. Детермінована обробка аварійних каналів
        | ex::let_error([](TelemetryError err) {
            std::string err_msg = "НЕВІДОМА_ПОМИЛКА";
            if (err == TelemetryError::CorruptedChecksum) err_msg = "ПОМИЛКА_КОНТРОЛЬНОЇ_СУМИ";
            if (err == TelemetryError::SensorDataOutOfRange) err_msg = "ДАНІ_ПОЗА_ДІАПАЗОНОМ";

            std::cerr << std::format("[ALERT] Помилка обробки телеметрії: {}\n", err_msg);
            return ex::just(false);
        });
}
