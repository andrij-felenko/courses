// cli_license.cpp — вивід ліцензійної таблиці з Flash у послідовну консоль.
//
// Формат навмисно колонковий: оператор читає його з термінала, а тестовий стенд
// розбирає той самий вивід і звіряє з паспортом SBOM.
#include "cli_license.hpp"

#include <array>
#include <cstddef>
#include <format>

#include "license_table.hpp"

namespace fw {
namespace {

// Шапку друкуємо готовим рядком: і std::format, і printf рахують ширину поля
// в БАЙТАХ, а українські слова в UTF-8 займають їх удвічі більше, ніж символів.
// Дані таблиці чисто ASCII, тому їх ширину рахувати можна.
constexpr std::string_view kHeader =
    "Компонент                  Версія    Ліцензія                               Правовласник\r\n";
constexpr std::string_view kRule =
    "-------------------------- --------- -------------------------------------- ------------\r\n";

// Один рядок таблиці. Форматування йде у власний буфер на стеку:
// std::format_to_n не виділяє пам'яті, на відміну від std::format.
void print_row(const LicenseEntry& entry, WriterRef out)
{
    std::array<char, 200> buffer{};
    const auto result = std::format_to_n(
        buffer.data(), buffer.size() - 2,
        "{:<{}.{}} {:<{}.{}} {:<{}.{}} {}",
        entry.name, kNameColumn, kNameColumn,
        entry.version, kVersionColumn, kVersionColumn,
        entry.spdx, kLicenseColumn, kLicenseColumn,
        entry.holder);

    // result.out показує, скільки справді лягло в буфер; result.size — скільки
    // знадобилося б. Задовге поле правовласника просто обрізається.
    const auto written = static_cast<std::size_t>(result.out - buffer.data());
    out(std::string_view(buffer.data(), written));
    out("\r\n");
}

void print_card(const LicenseEntry& entry, WriterRef out)
{
    out("\r\nКомпонент   : ");
    out(entry.name);
    out("\r\nВерсія      : ");
    out(entry.version);
    out("\r\nЛіцензія    : ");
    out(entry.spdx);
    out("\r\nПравовласник: ");
    out(entry.holder);
    out("\r\nЗастереження: ");
    out(entry.notice.value_or("окремих умов немає"));
    out("\r\n\r\n");
}

}  // namespace

CommandResult license_command(std::string_view args, WriterRef out)
{
    if (!args.empty()) {
        const LicenseEntry* entry = find_license(args);
        if (entry == nullptr) {
            out("\r\nкомпонента з такою назвою в образі немає; "
                "виконайте license без аргументів\r\n");
            return std::unexpected(ConsoleError::BadArgument);
        }
        print_card(*entry, out);
        return {};
    }

    out("\r\n=== СКЛАД ПРОШИВКИ ТА ЛІЦЕНЗІЇ (SBOM) ===\r\n");
    out(kHeader);
    out(kRule);

    for (const LicenseEntry& entry : kLicenses) {
        print_row(entry, out);
    }

    out(kRule);

    std::array<char, 96> footer{};
    const auto result = std::format_to_n(footer.data(), footer.size(),
                                         "Компонентів: {}. Подробиці: license <назва>.\r\n",
                                         kLicenses.size());
    out(std::string_view(footer.data(),
                         static_cast<std::size_t>(result.out - footer.data())));
    out("Повні тексти ліцензій — в інструкції користувача та за письмовим запитом.\r\n\r\n");
    return {};
}

CommandResult about_command(std::string_view args, WriterRef out)
{
    if (!args.empty()) {
        out("\r\nabout аргументів не приймає\r\n");
        return std::unexpected(ConsoleError::BadArgument);
    }

    out("\r\nВиріб    : ");
    out(kProductName);
    out("\r\nПрошивка : ");
    out(kProductVersion);
    out("\r\nЗібрано  : " __DATE__ " " __TIME__);
    // Хеш паспорта прив'язує консольну відповідь до підписаного метапакета OTA:
    // стенд звіряє цей рядок із serialNumber та hashes у firmware.cdx.json.
    out("\r\nSBOM     : SHA-256 ");
    out(kSbomSha256);
    out("\r\nСклад компонентів: команда license\r\n\r\n");
    return {};
}

}  // namespace fw
