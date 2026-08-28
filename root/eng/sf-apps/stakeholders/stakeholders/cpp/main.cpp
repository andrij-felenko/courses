#include <string>
#include <vector>
#include <set>
#include <cstdio>

// Якісний атрибут, про який дбає стейкхолдер.
enum class Attribute { Availability, Modifiability, Performance, Security, Cost };

struct Stakeholder {
    std::string name;
    int         power;      // 1..5 — наскільки може впливати на рішення
    Attribute   concern;    // головна турбота цієї людини
};

const char* attrName(Attribute a) {
    switch (a) {
        case Attribute::Availability:  return "доступність";
        case Attribute::Modifiability: return "змінюваність";
        case Attribute::Performance:   return "швидкодія";
        case Attribute::Security:      return "безпека";
        case Attribute::Cost:          return "вартість";
    }
    return "?";
}

int main() {
    std::vector<Stakeholder> reg = {
        {"Замовник",      5, Attribute::Cost},
        {"Оператор",      2, Attribute::Availability},   // тихий, але з великою ставкою
        {"Супровід",      3, Attribute::Modifiability},
        {"Аудитор",       4, Attribute::Security},
        {"Користувач",    3, Attribute::Performance},
    };

    // Атрибути, які архітектура вже свідомо закрила рішеннями.
    std::set<Attribute> covered = {
        Attribute::Cost, Attribute::Modifiability, Attribute::Performance
    };

    // Знаходимо турботи без відповіді — саме тут ховаються майбутні провали.
    for (const Stakeholder& s : reg) {
        if (covered.find(s.concern) == covered.end()) {
            std::printf("НЕ ЗАКРИТО: %-10s (вплив %d) дбає про %s\n",
                        s.name.c_str(), s.power, attrName(s.concern));
        }
    }
    return 0;
}
