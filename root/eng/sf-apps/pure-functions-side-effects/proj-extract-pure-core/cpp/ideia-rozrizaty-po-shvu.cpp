// ── знімок політики: колишні глобальні змінні, тепер явний вхід ──
struct Pricing {
    double taxRate      = 0.20;
    double freeShipFrom = 500.0;
    double shipCost     = 49.0;
};

// ── результат: розкладка, а не голе число ──
struct Totals {
    double subtotal;
    double discount;    // сума, на яку знижено
    double tax;
    double shipping;
    double total;
};
