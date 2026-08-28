void test_static_ring_buffer() {
    // 1. Ініціалізація з масиву: T = double, Capacity = 4
    double raw_sensor_data[] = {23.4, 24.1, 23.9, 25.0};
    StaticRingBuffer buffer(raw_sensor_data);

    static_assert(buffer.capacity() == 4, "Місткість повинна бути обчислена точно як 4");
    std::cout << "Створено буфер місткістю " << buffer.capacity() 
              << ", перший елемент: " << buffer[0] << '\n';

    // 2. Ініціалізація списком: T = int, Capacity = 32
    StaticRingBuffer init_buffer = {100, 200, 300};
    static_assert(init_buffer.capacity() == 32, "Дефолтна місткість списку = 32");

    // 3. Ініціалізація ітераторами: T = double, Capacity = 64
    StaticRingBuffer iter_buffer(std::begin(raw_sensor_data), std::end(raw_sensor_data));
    static_assert(iter_buffer.capacity() == 64, "Дефолтна місткість ітераторів = 64");
}
