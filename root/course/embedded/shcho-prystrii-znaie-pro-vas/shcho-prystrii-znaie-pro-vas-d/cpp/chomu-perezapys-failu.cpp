// Наївна спроба затерти файл нулями на рівні C++
#include <fstream>
#include <array>

void naiveSanitizeFile() {
    std::fstream file("/spiffs/token.dat", std::ios::in | std::ios::out | std::ios::binary);
    if (file.is_open()) {
        std::array<uint8_t, 64> zeros{};
        file.write(reinterpret_cast<const char*>(zeros.data()), zeros.size());
        file.close();
    }
}
