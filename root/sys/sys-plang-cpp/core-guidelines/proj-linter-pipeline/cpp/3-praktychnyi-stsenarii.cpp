// Легасі-код на C++ із накопиченими порушеннями Core Guidelines
#include <cstdio>
#include <cstdlib>

struct TelemetryPacket {
    double timestamp;
    float value;
    int status_flags;
};

int filter_active_packets(const TelemetryPacket* input, int count, 
                          TelemetryPacket*& output, int& out_count) {
    // Дефект 1: ES.20 (неініціалізовані змінні)
    int active;
    int error_code;

    // Дефект 2: I.11 та Bounds.1 (сирий вказівник + int замість std::span)
    if (input == nullptr || count <= 0) {
        return -1;
    }

    // Дефект 3: R.10 та R.3 (сире виділення пам'яті в купі з неявним володінням)
    output = new TelemetryPacket[count];

    active = 0;
    for (int i = 0; i < count; ++i) {
        // Дефект 4: ES.46 (звужувальне перетворення при бітовій масці)
        short flag_masked = input[i].status_flags & 0x01;
        if (flag_masked != 0) {
            output[active] = input[i];
            active++;
        }
    }

    out_count = active;
    
    // Дефект 5: Type.1 (C-варіативна функція printf)
    std::printf("Extracted %d active packets\n", active);

    return 0;
}
