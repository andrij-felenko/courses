#include <concepts>
#include <cstdint>
#include <string_view>
#include <type_traits>

// Концепт, що перевіряє структурний контракт сенсорного вимірювання
template<typename T>
concept SensorReading = requires(const T& r) {
    { r.timestamp_ms } -> std::convertible_to<std::uint64_t>;
    { r.raw_value }    -> std::floating_point;
    { r.sensor_id }    -> std::convertible_to<std::string_view>;
    { r.is_valid() }   -> std::same_as<bool>;
};

// Концепт для приймача оброблених повідомлень
template<typename Sink, typename Data>
concept TelemetrySink = requires(Sink& sink, const Data& data) {
    { sink.consume(data) } -> std::same_as<void>;
};
