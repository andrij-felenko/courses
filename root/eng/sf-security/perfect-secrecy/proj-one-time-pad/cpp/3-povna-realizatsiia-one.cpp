#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <random>
#include <stdexcept>
#include <iomanip>
#include <algorithm>

class OneTimePad {
public:
    // Генерація криптографічно стійкого ключа через std::random_device (апаратна ентропія)
    static std::vector<uint8_t> generateKey(size_t length) {
        if (length == 0) {
            throw std::invalid_argument("Довжина ключа має бути додатною");
        }
        std::vector<uint8_t> key(length);
        std::random_device rd;
        
        // Заповнення буфера випадковими 32-бітними словами системної ентропії
        size_t i = 0;
        while (i < length) {
            uint32_t val = rd();
            for (size_t b = 0; b < 4 && i < length; ++b, ++i) {
                key[i] = static_cast<uint8_t>(val & 0xFF);
                val >>= 8;
            }
        }
        return key;
    }

    // Симетричне перетворення XOR над буферами однакової довжини
    static std::vector<uint8_t> transform(std::span<const uint8_t> data, std::span<const uint8_t> key) {
        if (data.size() != key.size()) {
            throw std::invalid_argument("Розміри даних та ключа мають збігатися");
        }
        std::vector<uint8_t> result(data.size());
        for (size_t i = 0; i < data.size(); ++i) {
            result[i] = data[i] ^ key[i];
        }
        return result;
    }

    // Безпечне затирання секретного ключа в оперативній пам'яті
    static void secureWipe(std::span<uint8_t> buffer) {
        volatile uint8_t* p = buffer.data();
        for (size_t i = 0; i < buffer.size(); ++i) {
            p[i] = 0;
        }
    }
};

int main() {
    std::string_view msgText = "СЕКРЕТНИЙ_НАКАЗ_АТАКА_О_ПЯТИЙ";
    std::span<const uint8_t> message(reinterpret_cast<const uint8_t*>(msgText.data()), msgText.size());

    std::cout << "Відкритий текст (" << message.size() << " байтів): " << msgText << "\n";

    // 1. Генерація одноразового ключа
    std::vector<uint8_t> key = OneTimePad::generateKey(message.size());

    // 2. Шифрування
    std::vector<uint8_t> ciphertext = OneTimePad::transform(message, key);
    std::cout << "Шифротекст (hex): ";
    for (size_t i = 0; i < std::min<size_t>(16, ciphertext.size()); ++i) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(ciphertext[i]);
    }
    std::cout << "...\n" << std::dec;

    // 3. Дешифрування
    std::vector<uint8_t> decrypted = OneTimePad::transform(ciphertext, key);
    std::string_view decText(reinterpret_cast<const char*>(decrypted.data()), decrypted.size());
    std::cout << "Розшифровано:     " << decText << "\n";

    // 4. Очищення ключа
    OneTimePad::secureWipe(key);

    return 0;
}
