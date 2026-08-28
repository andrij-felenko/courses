struct Header {
    uint32_t magic = 0xDEADBEEF;
    uint16_t version = 1;
};

int main() {
    BinaryStreamWriter writer;

    Header hdr;
    writer.write(hdr); // Шлях 1: 6 байтів прямого копіювання

    std::string device_name = "LiDAR-Front";
    writer.write(device_name); // Шлях 2: 4 байти довжини + 11 байтів тексту

    std::vector<int32_t> raw_points = {100, 250, -45, 890};
    writer.write(raw_points); // Шлях 3: 4 байти розміру + 4*4 байти чисел

    std::cout << "Загальний розмір серіалізованого буфера: " 
              << writer.size_bytes() << " байтів\n";
    return 0;
}
