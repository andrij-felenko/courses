// (2) ПОЛІТИКА: та сама поведінка — компайл-тайм-ТИП-параметр.
//     Який алгоритм — вирішується під час КОМПІЛЯЦІЇ; віртуальних викликів нема.
struct VipDiscount {
    static double discount(double total) { return total * 0.20; }
};
struct NoDiscount {
    static double discount(double total) { return 0.0; }
};

template <class Policy>                                 // поведінка приходить ТИПОМ
struct Order {
    double total;
    double final_price() const {
        return total - Policy::discount(total);         // підставлено ще до запуску
    }
};

// вибір робиться в типі: компілятор згортає окрему версію під кожну політику
Order<VipDiscount> a{1000};   a.final_price();          // 800
Order<NoDiscount>  b{1000};   b.final_price();          // 1000
