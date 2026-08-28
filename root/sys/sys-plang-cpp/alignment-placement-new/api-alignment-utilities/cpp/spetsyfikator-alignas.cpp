// 1. Примусове вирівнювання окремої змінної
alignas(16) float vector4[4];

// 2. Використання типу як аргументу
alignas(double) char raw_buffer[sizeof(double)];

// 3. Вирівнювання поля структури
struct Node {
    char tag;
    alignas(64) int counter; // розміщує counter на початку 64-байтної кеш-лінії
};

// 4. Вирівнювання цілого типу
struct alignas(32) AVXData {
    float values[8];
};
