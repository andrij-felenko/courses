# Практика: Обчислення інтернет-контрольної суми (IPv4)

Мережеві протоколи, такі як IPv4, TCP та UDP, досі використовують 16-бітну арифметику оберненого коду для перевірки цілісності даних. Це надійний, швидкий та незалежний від порядку байтів (endianness) метод. Давайте напишемо сучасний C++17 скрипт, який обчислює та перевіряє контрольну суму (Internet Checksum) для заголовка IPv4.

Алгоритм обчислення дуже простий, але потребує уважності до деталей:
1. Заголовок розбивається на 16-бітні слова.
2. Усі слова додаються у 32-бітний акумулятор. Це дозволяє перехоплювати всі переноси, що виникають під час додавання.
3. Коли всі слова додані, старші 16 бітів акумулятора (усі накопичені переноси) зсуваються вправо і додаються до молодших 16 бітів (виконується циклічний перенос, end-around carry). Цей крок повторюється, доки в старших 16 бітах не залишиться нулів.
4. Результат інвертується (побітове NOT).

Нижче наведена структура програми, що складається з 5 компонентів: визначення структур, функція обчислення суми, створення пакета, валідація та точка входу.

```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>
#include <numeric>

// 1. Визначення структури для імітації заголовка IPv4
// (спрощений варіант для демонстрації обчислень)
struct IPv4Header {
    uint8_t  version_ihl;       // Версія та довжина заголовка
    uint8_t  tos;               // Тип сервісу
    uint16_t total_length;      // Загальна довжина
    uint16_t identification;    // Ідентифікатор
    uint16_t flags_frag_offset; // Прапорці та зміщення фрагмента
    uint8_t  ttl;               // Час життя
    uint8_t  protocol;          // Протокол (напр., TCP, UDP)
    uint16_t checksum;          // Контрольна сума
    uint32_t src_ip;            // IP-адреса відправника
    uint32_t dest_ip;           // IP-адреса отримувача
};

// 2. Функція обчислення контрольної суми в оберненому коді
uint16_t calculate_internet_checksum(const uint16_t* data, size_t length_in_bytes) {
    uint32_t sum = 0;
    size_t num_words = length_in_bytes / 2;

    // Додаємо всі 16-бітні слова
    for (size_t i = 0; i < num_words; ++i) {
        sum += data[i];
    }

    // Якщо довжина непарна, додаємо останній байт, доповнений нулями
    if (length_in_bytes % 2 != 0) {
        const uint8_t* byte_data = reinterpret_cast<const uint8_t*>(data);
        uint16_t last_word = static_cast<uint16_t>(byte_data[length_in_bytes - 1]) << 8;
        sum += last_word;
    }

    // Виконуємо циклічний перенос (end-around carry)
    // Поки є біти переносу вище 16-го розряду, зміщуємо їх і додаємо до молодших 16 біт
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }

    // Інвертуємо результат
    return static_cast<uint16_t>(~sum);
}

// 3. Функція створення пакета
std::vector<uint8_t> create_dummy_packet() {
    // Симуляція реального 20-байтового IP-заголовка
    // Дані взяті з класичного прикладу RFC 1071
    std::vector<uint8_t> packet = {
        0x45, 0x00, 0x00, 0x73, // Ver/IHL, ToS, Total Len
        0x00, 0x00, 0x40, 0x00, // ID, Flags/Offset
        0x40, 0x11, 0x00, 0x00, // TTL, Protocol, Checksum (поки 0)
        0xc0, 0xa8, 0x00, 0x01, // Src IP: 192.168.0.1
        0xc0, 0xa8, 0x00, 0xc7  // Dest IP: 192.168.0.199
    };
    return packet;
}

// 4. Функція валідації цілісності
bool validate_packet(const std::vector<uint8_t>& packet) {
    const uint16_t* data_ptr = reinterpret_cast<const uint16_t*>(packet.data());
    uint16_t validation_sum = calculate_internet_checksum(data_ptr, packet.size());
    
    // В арифметиці оберненого коду, правильний пакет при повному додаванні
    // (включно із самою сумою) і подальшій інверсії повинен дати 0x0000.
    // (Або сума до інверсії дає 0xFFFF, тобто від'ємний нуль -0)
    return validation_sum == 0x0000;
}

// 5. Точка входу (Main)
int main() {
    auto packet = create_dummy_packet();
    const uint16_t* data_ptr = reinterpret_cast<const uint16_t*>(packet.data());

    std::cout << "--- Internet Checksum (Ones' Complement) ---" << std::endl;

    // Обчислення
    uint16_t checksum = calculate_internet_checksum(data_ptr, packet.size());
    std::cout << "Обчислена контрольна сума: 0x" 
              << std::hex << std::setw(4) << std::setfill('0') << checksum << std::endl;

    // Вставляємо обчислену суму в пакет (зміщення 10 байт)
    // Увага: на реальних машинах x86 тут слід зважати на endianness,
    // проте для демонстрації алгоритму працюємо з прямим розміщенням.
    packet[10] = checksum & 0xFF;         // Молодший байт
    packet[11] = (checksum >> 8) & 0xFF;  // Старший байт

    // Валідація
    bool is_valid = validate_packet(packet);
    std::cout << "Результат валідації (непошкоджений пакет): " 
              << (is_valid ? "Успішно" : "Помилка") << std::endl;

    // Симуляція пошкодження даних (перевертаємо один біт)
    packet[15] ^= 0x01;
    bool is_valid_after_corruption = validate_packet(packet);
    std::cout << "Результат валідації (пошкоджений пакет): " 
              << (is_valid_after_corruption ? "Успішно" : "Помилка (Дані пошкоджено!)") << std::endl;

    return 0;
}
```

Коли код виконується, ви побачите, що обчислена сума ідеально балансує пакет. Під час валідації приймач просто проганяє ту саму функцію на отриманому буфері. Оскільки `~sum` було записано у пакет, нове підсумовування додасть саму суму до решти даних, що в результаті дасть `0xFFFF` (усі одиниці). Після фінальної інверсії в тілі функції ми отримаємо `0x0000`, що підтверджує: пакет прибув неушкодженим. Пошкодження навіть одного біта руйнує цей баланс.
