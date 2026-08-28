#include <map>

// Розклад визнання: правило таблицею. Ключ — тип товару,
// значення — зсуви часток у днях від дати підписання.
inline const std::unordered_map<std::string, std::vector<int>>& schedules() {
    static const std::unordered_map<std::string, std::vector<int>> table = {
        {"word-processor", {0}},
        {"database",       {0}},
        {"spreadsheet",    {0, 60, 90}},
    };
    return table;
}

// Ділення з округленням донизу — щоб залишок ніколи не був від'ємним.
inline Money floorDiv(Money a, Money b) {
    Money q = a / b;                                    // у C++ ділення цілих усікає до нуля
    if (a % b != 0 && ((a < 0) != (b < 0))) --q;
    return q;
}

// Ділимо суму на n часток так, щоб їхня сума ТОЧНО дорівнювала цілому.
// Залишок (менший за n копійок) роздаємо в останні частки.
inline std::vector<Money> splitEvenly(Money total, std::size_t n) {
    if (n == 0) throw std::logic_error("порожній розклад");
    const Money base = floorDiv(total, static_cast<Money>(n));
    Money rest = total - base * static_cast<Money>(n);  // 0 ≤ rest < n
    std::vector<Money> parts(n, base);
    for (std::size_t i = n; rest > 0; --rest) parts[--i] += 1;
    return parts;
}

class ProductModule {
public:
    explicit ProductModule(const SalesData& d) : d_(d) {}

    const std::string& kindOf(Id productId) const {
        const Product* p = d_.products.find(productId);
        if (!p) throw std::logic_error("немає товару " + std::to_string(productId));
        return p->kind;
    }
private:
    const SalesData& d_;
};

class ContractModule {
public:
    explicit ContractModule(SalesData& d) : d_(d) {}

    void calculateRecognitions(Id contractId) {
        const Contract* c = d_.contracts.find(contractId);   // один доступ, не перебір
        if (!c) throw std::logic_error("немає контракту " + std::to_string(contractId));
        const Money revenue = c->revenue;         // значення забираємо ЗАРАЗ: покажчик
        const Day   signedOn = c->signedOn;       // дійсний лише до наступної вставки
        const std::string kind = ProductModule(d_).kindOf(c->productId);

        auto it = schedules().find(kind);
        if (it == schedules().end()) throw std::logic_error("немає розкладу: " + kind);
        const std::vector<int>& offsets = it->second;

        dropRecognitions(contractId);             // повторний виклик не подвоює рядки
        const std::vector<Money> parts = splitEvenly(revenue, offsets.size());
        for (std::size_t i = 0; i < offsets.size(); ++i)
            d_.recognitions.insert(Recognition{d_.nextTempId--, contractId,
                                               parts[i], signedOn + offsets[i]});
    }

    Money recognizedAsOf(Id contractId, Day asOf) const {
        Money sum = 0;
        for (std::size_t i : d_.recognitions.rowsWith(contractId)) {   // тільки свої рядки
            if (!d_.recognitions.alive(i)) continue;
            const Recognition& r = d_.recognitions.at(i);
            if (r.on <= asOf) sum += r.amount;
        }
        return sum;
    }

    // Підсумок за НАБОРОМ: один прохід по визнаннях, решта — доступи за ключем.
    std::map<std::string, Money> recognizedByKind(Day asOf) const {
        std::map<std::string, Money> total;
        ProductModule products(d_);
        for (std::size_t i = 0; i < d_.recognitions.size(); ++i) {
            if (!d_.recognitions.alive(i)) continue;
            const Recognition& r = d_.recognitions.at(i);
            if (r.on > asOf) continue;
            const Contract* c = d_.contracts.find(r.contractId);
            if (!c) continue;                       // осиротіле визнання — не наша справа
            total[products.kindOf(c->productId)] += r.amount;
        }
        return total;
    }

private:
    void dropRecognitions(Id contractId) {
        for (std::size_t i : d_.recognitions.rowsWith(contractId))
            if (d_.recognitions.alive(i)) d_.recognitions.erase(d_.recognitions.at(i).id);
    }

    SalesData& d_;
};
