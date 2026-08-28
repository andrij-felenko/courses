// src/main.cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <tinyxml2.h>
#include "miniz.h"

int main() {
    constexpr std::string_view raw_xml = 
        "<telemetry version=\"1.0\">\n"
        "    <sensor name=\"temperature\" value=\"24.5\" unit=\"celsius\"/>\n"
        "    <sensor name=\"pressure\" value=\"1013.25\" unit=\"hPa\"/>\n"
        "</telemetry>";

    tinyxml2::XMLDocument doc;
    const tinyxml2::XMLError err = doc.Parse(raw_xml.data(), raw_xml.size());
    if (err != tinyxml2::XML_SUCCESS) {
        std::cerr << "Помилка розбору XML: " << doc.ErrorStr() << "\n";
        return 1;
    }

    const auto* root = doc.FirstChildElement("telemetry");
    if (!root) {
        std::cerr << "Відсутній кореневий елемент telemetry\n";
        return 1;
    }

    std::cout << "Успішно розібрано пакет телеметрії версії: " 
              << root->Attribute("version") << "\n";

    // Демонстрація стиснення через вендорений Miniz
    const uLong bound = compressBound(static_cast<uLong>(raw_xml.size()));
    std::vector<unsigned char> compressed_buffer(bound);
    uLong compressed_size = bound;

    const int status = compress(
        compressed_buffer.data(),
        &compressed_size,
        reinterpret_cast<const unsigned char*>(raw_xml.data()),
        static_cast<uLong>(raw_xml.size())
    );

    if (status != Z_OK) {
        std::cerr << "Помилка стиснення: " << status << "\n";
        return 1;
    }

    compressed_buffer.resize(compressed_size);
    std::cout << "Стиснено: " << raw_xml.size() << " байтів -> " 
              << compressed_buffer.size() << " байтів.\n";

    return 0;
}
