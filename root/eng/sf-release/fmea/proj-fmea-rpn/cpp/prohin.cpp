void show(const std::string& title, const std::vector<Entry>& rows, bool before) {
    std::cout << "\n" << title << "\n";
    std::cout << std::left << std::setw(3) << "#" << std::setw(7) << "id"
              << std::right << std::setw(3) << "S" << std::setw(3) << "O"
              << std::setw(3) << "D" << std::setw(6) << "RPN" << std::setw(7) << "AP"
              << "  вид відмови\n";
    int i = 1;
    for (const Entry& e : rows) {
        const Rating r = before ? e.before : e.current();
        std::cout << std::left << std::setw(3) << i++ << std::setw(7) << e.id
                  << std::right << std::setw(3) << r.s << std::setw(3) << r.o
                  << std::setw(3) << r.d << std::setw(6) << r.rpn()
                  << std::setw(7) << name(r.ap()) << "  " << e.mode << "\n";
    }
}

int main() {
    std::vector<Entry> reg = {
        {.id = "P-01", .item = "шлюз оплати",
         .function = "провести платіж і повернути відповідь",
         .mode = "відповідь не прийшла за таймаут",
         .cause = "шлюз перевантажений у пікові години",
         .effect = "замовлення не оформлено, продаж утрачено",
         .control = "сплеск помилок видно на панелі",
         .before = Rating(SEVERITY("втрата-друг"), OCCURRENCE("1:2000"),
                          DETECTION("на-місці"))},
        {.id = "P-02", .item = "списання коштів",
         .function = "списати суму замовлення рівно один раз",
         .mode = "суму списано двічі",
         .cause = "клієнт повторив запит, ключа ідемпотентності немає",
         .effect = "з клієнта взято вдвічі; повернення, скарга, втрата довіри",
         .control = "дізнаємось, лише коли клієнт поскаржиться",
         .before = Rating(SEVERITY("закон"), OCCURRENCE("1:1млн"),
                          DETECTION("вибірково"))},
        {.id = "P-03", .item = "вітрина товару",
         .function = "показувати чинну ціну",
         .mode = "показано стару ціну з кешу",
         .cause = "кеш цін не скинуто після переоцінки",
         .effect = "продаж нижче собівартості, втрата маржі",
         .control = "жодного: помітно тільки на квартальній звірці",
         .before = Rating(SEVERITY("прикро"), OCCURRENCE("1:500"),
                          DETECTION("немає"))},
    };

    show("ЧЕРГА ЗА ГОЛИМ RPN:",      by_rpn(reg, /*before=*/true), /*before=*/true);
    show("ЧЕРГА ЗА ПРІОРИТЕТОМ ДІЙ:", by_priority(reg, true), true);
