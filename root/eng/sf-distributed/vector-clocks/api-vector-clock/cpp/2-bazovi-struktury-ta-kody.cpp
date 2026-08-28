#include <cstdint>
#include <cstddef>

using NodeId = uint32_t;
using Counter = uint64_t;

// Окремий запис версійного вектора для конкретного актора
struct Entry {
    NodeId node_id{0};
    Counter counter{0};
    uint64_t physical_wall_time_ms{0}; // UTC мітка в мілісекундах
};

// Коди помилок та статусів бібліотеки
enum class Status : int32_t {
    Ok = 0,
    NullPtr = -1,
    OutOfMemory = -2,
    BufferTooSmall = -3,
    CorruptedData = -4,
    NodeNotFound = -5,
    CapacityExceeded = -6,
    CounterOverflow = -7
};
