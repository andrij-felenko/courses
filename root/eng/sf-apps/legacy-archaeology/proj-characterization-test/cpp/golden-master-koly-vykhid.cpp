#include <vector>
#include <sstream>
#include <fstream>
#include <iomanip>

struct InvoiceLine { std::string sku; int qty; double lineTotal; };
struct Invoice {
    std::vector<InvoiceLine> lines;
    double discount;
    double vat;
    double total;
};

// Серіалізація у СТАБІЛЬНИЙ, детермінований текст — це серце golden-master.
// Кожне рішення тут захищає нас від хибних провалів (див. пастки нижче):
//  - фіксований формат чисел (2 знаки), щоб 11.5 і 11.50 не розійшлись;
//  - явний, а не "як вийде", порядок рядків;
//  - жодних адрес, дат генерації, вказівників — нічого недетермінованого.
std::string renderInvoice(const Invoice& inv) {
    std::ostringstream os;
    os << std::fixed << std::setprecision(2);
    for (const auto& l : inv.lines)
        os << "LINE " << l.sku << " x" << l.qty
           << " = " << l.lineTotal << "\n";
    os << "DISCOUNT " << inv.discount << "\n";
    os << "VAT "      << inv.vat      << "\n";
    os << "TOTAL "    << inv.total    << "\n";
    return os.str();
}

// Ядро approval-перевірки: якщо еталона ще нема — створюємо його (перший
// прогін "затверджує" поточну поведінку); якщо є — звіряємо байт-у-байт.
bool approve(const std::string& name, const std::string& actual) {
    std::string path = std::string("golden/") + name + ".txt";
    std::ifstream in(path);
    if (!in) {                                  // еталона нема -> запам'ятати
        std::ofstream out(path);
        out << actual;
        std::cerr << "APPROVED (new): " << path << "\n";
        return true;                            // перший раз завжди "проходить"
    }
    std::stringstream buf; buf << in.rdbuf();
    std::string expected = buf.str();
    if (expected == actual) return true;
    // розбіжність: показуємо, ЩО поїхало (у житті тут diff-інструмент)
    std::cerr << "GOLDEN MISMATCH " << name << "\n--- expected ---\n"
              << expected << "--- actual ---\n" << actual;
    return false;
}
