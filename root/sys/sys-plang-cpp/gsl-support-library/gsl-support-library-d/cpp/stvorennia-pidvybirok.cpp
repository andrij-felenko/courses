#include <gsl/gsl>
#include <array>

// Робота через типобезпечний зріз gsl::span
void parse_payload_cpp(gsl::span<const gsl::byte> packet) {
    if (packet.size() < 16) return;

    // Створення піддіапазону: автоматична валідація зміщення та довжини
    auto payload = packet.subspan(8, packet.size() - 12);
    
    // Статичний зріз фіксованого розміру
    auto header = packet.first<8>(); 
    (void)header;
}
