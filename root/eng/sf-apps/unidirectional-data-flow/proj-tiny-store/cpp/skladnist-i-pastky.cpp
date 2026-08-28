struct Deal       { long long amount; long long rate; };
struct DealClosed { Deal deal; };                  // ще одна дія

struct State {
    Field     entered = Field::Usd;
    long long amount  = 0, rate = 92;
    std::shared_ptr<const std::vector<Deal>> deals  // великий шматок
        = std::make_shared<const std::vector<Deal>>();
};

// гілка переходу, що додає угоду: клонуємо лише список, і лише тут
[&](const DealClosed& d) {
    auto next = std::make_shared<std::vector<Deal>>(*n.deals);
    next->push_back(d.deal);
    n.deals = std::move(next);
}
