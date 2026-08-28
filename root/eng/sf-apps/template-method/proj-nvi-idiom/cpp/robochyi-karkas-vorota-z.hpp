#include <string>
#include <vector>
#include <stdexcept>
#include <cassert>

struct Field { std::string key, value; };

class Report {
public:
    // ВОРОТА: публічний НЕвіртуальний каркас. Нащадок його не перевизначить.
    std::string render(const std::vector<Field>& fields) const {
        // — передумова: далі крок нащадка вільно припускає, що список не порожній
        if (fields.empty())
            throw std::invalid_argument("render: порожній список полів");

        std::string out = header(fields.size());     // спільний крок — завжди

        std::string body = renderBody(fields);        // ← ДІРКА: код нащадка

        // — післяумова: перевіряємо те, що нащадок ОБІЦЯВ віддати
        assert(!body.empty()          && "renderBody вернув порожнє тіло");
        assert(body.back() != '\n'    && "тіло не має завершуватись переносом");

        out += body;
        out += footer();                              // спільний крок — завжди

        // — інваріант результату: звіт завжди починається заголовком
        assert(out.rfind(MAGIC, 0) == 0 && "звіт втратив заголовок");
        return out;
    }

    virtual ~Report() = default;   // публічний віртуальний — бо видаляємо через Report*

private:
    // ДІРКА: приватна ВІРТУАЛЬНА. Нащадок МУСИТЬ дати; покликати ззовні не може.
    virtual std::string renderBody(const std::vector<Field>& fields) const = 0;

    // ЗАМКНЕНІ спільні кроки — приватні невіртуальні, однакові для всіх.
    static constexpr const char* MAGIC = "=== REPORT ===";
    std::string header(std::size_t n) const {
        return std::string(MAGIC) + " (fields: " + std::to_string(n) + ")\n";
    }
    std::string footer() const { return "\n=== END ===\n"; }
};
