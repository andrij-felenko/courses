#include <memory>

struct SensorNode {
    int value{0};
    void poll() { value++; }
};

void process_node() {
    auto node = std::make_shared<SensorNode>();
    
    // Отримуємо сире посилання на керований об'єкт
    SensorNode& ref = *node;

    // Скидаємо розумний вказівник (або передаємо його в інший потік, де він знищується)
    node.reset(); 

    // Use-After-Free: об'єкт SensorNode знищено методом reset()!
    ref.poll(); 
}
