#include <cassert>
#include <functional>
#include <iostream>

static bool throwsDomain(const std::function<void()>& fn) {
    try { fn(); } catch (const DomainError&) { return true; }
    return false;
}

int main() {
    // 1. постійний клієнт дістає знижку, а склад меншає
    {
        Product laptop("SKU-1", Money::of(3'000'000, "UAH"), 5);   // 30 000.00, 5 шт
        Customer gold("C-1", Tier::Gold);

        Order order("O-1", "C-1");
        order.addLine(laptop, 2);
        order.place(gold);

        assert(order.status() == Status::Placed);
        assert(order.total() == Money::of(5'400'000, "UAH"));      // 60 000 − 10%
        assert(laptop.stock() == 3);                               // 5 − 2
    }
    // 2. вартові не пускають неможливий стан
    {
        Customer reg("C-1", Tier::Regular);

        Order empty("O-2", "C-1");
        assert(throwsDomain([&]{ empty.place(reg); }));            // порожнє оформити не можна

        Product p("SKU-1", Money::of(1000, "UAH"), 10);
        Order order("O-3", "C-1");
        order.addLine(p, 1);
        assert(throwsDomain([&]{ order.ship(); }));                // чернетку не відвантажити
        order.place(reg);
        assert(throwsDomain([&]{ order.place(reg); }));            // оформити двічі — не можна
    }
    std::cout << "усі перевірки пройдено — і жодної бази поруч\n";
    return 0;
}
