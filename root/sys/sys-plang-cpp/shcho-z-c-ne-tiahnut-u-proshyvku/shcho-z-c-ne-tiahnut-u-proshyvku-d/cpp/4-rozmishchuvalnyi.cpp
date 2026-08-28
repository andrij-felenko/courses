#include <cstdint>
#include <new> // Необхідний для розміщувального new

class SensorNode {
public:
    explicit constexpr SensorNode(uint32_t id) noexcept 
        : m_id(id), m_value(0.0f) {}

    [[nodiscard]] float read() const noexcept { return m_value; }

private:
    uint32_t m_id;
    float m_value;
};

/* Буфер потрібного розміру та вирівнювання у секції .bss */
alignas(SensorNode) static uint8_t node_buffer[sizeof(SensorNode)];

/* Конструювання об'єкта через placement new без динамічної купи */
SensorNode* init_sensor_node(uint32_t id) noexcept {
    return ::new (static_cast<void*>(node_buffer)) SensorNode(id);
}
