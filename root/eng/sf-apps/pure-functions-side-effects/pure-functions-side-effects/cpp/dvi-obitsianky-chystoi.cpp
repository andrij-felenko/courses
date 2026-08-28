// НЕЧИСТА: читає глобальний курс, пише в лог, міняє переданий об'єкт
double g_taxRate;                          // глобальний стан — прихований вхід

double totalPrice(Order& order) {          // Order& — не const, отже може змінитися
    double sum = 0.0;
    for (Item& it : order.items) {
        it.priceWithTax = it.price * (1.0 + g_taxRate);  // мутує вхід
        sum += it.priceWithTax * it.qty;
    }
    std::cout << "computed: " << sum << "\n";  // побічний ефект: вивід
    order.lastTotal = sum;                     // ще одна мутація входу
    return sum;
}
