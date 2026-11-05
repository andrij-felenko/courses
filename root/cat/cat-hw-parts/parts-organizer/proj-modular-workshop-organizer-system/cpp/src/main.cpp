#include "organizer_matrix.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=== C++ Модульна модель матриці органайзера та ESD-валідатор ===\n\n";

    using namespace organizer;

    // 1. Створення матриці касетного блоку під ряд номіналів E24
    // Кожна комірка має внутрішні габарити 50х40х38 мм
    OrganizerMatrix matrix(ESeries::E24, 50.0, 40.0, 38.0, 1.6);

    std::cout << "[1] Параметри модульної матриці (ряд E24):\n";
    std::cout << "  Кількість комірок:   " << matrix.columns() * matrix.rows() << " шт\n";
    std::cout << "  Розмірність сітки:   " << matrix.columns() << " колонок x " << matrix.rows() << " рядків\n";
    std::cout << "  Габарити корпусу:    " << std::fixed << std::setprecision(1)
              << matrix.total_width_mm() << " x " << matrix.total_length_mm() << " мм\n\n";

    // 2. Додавання компонентів до тестових комірок
    PartInfo screws_m3{
        "Гвинти М3х10 ISO 7380",
        12.0, 5.5, 5.5,
        150 // 150 штук у комірку A1
    };

    PartInfo chip_soic8{
        "Мікросхеми SOIC-8 (драйвери)",
        5.0, 6.0, 1.75,
        80 // 80 штук у комірку A2
    };

    matrix.set_part(0, 0, screws_m3);
    matrix.set_part(1, 0, chip_soic8);

    std::cout << "[2] Оцінка наповненості комірок:\n";
    for (size_t i = 0; i < 2; ++i) {
        const auto& c = matrix.cells()[i];
        std::cout << "  Комірка " << c.label() << ": "
                  << "необхідний об'єм = " << std::setprecision(0) << c.required_volume_mm3() << " мм³, "
                  << "місткість = " << c.capacity_volume_mm3() << " мм³, "
                  << "заповненість = " << std::setprecision(1) << c.fill_percentage() << "% "
                  << (c.is_overfilled() ? "[ПЕРЕПОВНЕНО]" : "[НОРМА]") << "\n";
    }
    std::cout << "\n";

    // 3. Валідація матеріалу за стандартом ESD IEC 61340-5-1
    // Перевіряємо два зразки: звичайний діелектричний ABS та антистатичний ESD-полімер
    EsdProfile normal_abs(1.0e14, 100.0);       // 10^14 Ом/кв (діелектрик)
    EsdProfile esd_conductive(2.5e7, 100.0);    // 2.5*10^7 Ом/кв (дисипативний)

    std::cout << "[3] Валідація електростатичної безпеки за IEC 61340-5-1:\n";

    auto test_material = [](std::string_view name, const EsdProfile& prof) {
        double t_decay = prof.calculate_decay_time(1000.0, 100.0);
        bool ok = prof.is_compliant(1000.0, 100.0);

        std::cout << "  Матеріал: " << name << "\n";
        std::cout << "    Опір:        " << std::scientific << std::setprecision(1)
                  << prof.surface_resistivity() << " Ом/кв\n";
        std::cout << "    Час спаду:   " << std::fixed << std::setprecision(4)
                  << t_decay << " с (норма <= " << kEsdMaxDecayTimeSec << " с)\n";
        std::cout << "    Відповідність стандарту: "
                  << (ok ? "ТАК (Безпечно для польових транзисторів)" : "НІ (Ризик трибоелектричного пробою)") << "\n";
    };

    test_material("Звичайний ABS (діелектрик)", normal_abs);
    test_material("Антистатичний ESD-полімер (дисипативний)", esd_conductive);

    return 0;
}
