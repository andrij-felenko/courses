#include <iostream>

namespace diagnostic_demo {

void process_data(bool flag) {
    int uninitialized_value;
    if (flag) {
        uninitialized_value = 100;
    }
    /* При flag == false змінна містить сміття, V-біти дорівнюють 0 */
    if (uninitialized_value > 50) {
        std::cout << "Condition met\n";
    }
}

} // namespace diagnostic_demo
