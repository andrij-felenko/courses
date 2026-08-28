#include <string>
#include <vector>
#include <limits>

// Внесок стратегії в ОДИН атрибут: вага стейкхолдера й корисність до/після (0..100).
struct Contribution {
    std::string attribute;
    double weight;   // наскільки атрибут важливий стейкхолдерам
    double before;   // корисність зараз
    double after;    // корисність, якщо стратегію впровадити
};

struct Strategy {
    std::string name;
    double cost;                            // вартість, тижні
    std::vector<Contribution> contribs;

    // CBAM: вигода = Σ вага·(корисність_після − корисність_до)
    double benefit() const {
        double sum = 0.0;
        for (const auto& c : contribs)
            sum += c.weight * (c.after - c.before);
        return sum;
    }

    double roi() const {
        return cost != 0.0 ? benefit() / cost
                           : std::numeric_limits<double>::infinity();
    }
};
