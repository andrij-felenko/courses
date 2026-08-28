#include <iostream>
#include <string>
#include <string_view>
#include <variant>
#include <tuple>
#include <utility>
#include <cstdint>
#include <type_traits>
#include <memory>
#include <chrono>

struct PingEvent {
    uint64_t timestamp;
    uint32_t sequence_id;
};

struct TelemetryEvent {
    uint64_t timestamp;
    double voltage;
    double current;
    double temperature;
};

struct CommandEvent {
    uint64_t timestamp;
    std::string command;
    int priority;
};

using EventVariant = std::variant<PingEvent, TelemetryEvent, CommandEvent>;
