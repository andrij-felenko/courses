// src/main.cpp
#include <iostream>
#include <string_view>
#include <vector>
#include "codec.h"

int main() {
    std::string_view raw_payload = "Telemetry_Packet_0x89A";
    std::vector<char> encoded(raw_payload.size() + 1);

    int status = legacy_encode(raw_payload.data(), raw_payload.size(),
                               encoded.data(), encoded.size());

    if (status >= 0) {
        std::cout << "Successfully encoded payload. Size: " << status << " bytes\n";
    } else {
        std::cerr << "Encoding failed!\n";
        return 1;
    }
    return 0;
}
