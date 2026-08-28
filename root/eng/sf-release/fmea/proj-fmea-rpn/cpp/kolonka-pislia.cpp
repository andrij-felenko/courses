    auto find = [&](const std::string& id) -> Entry& {
        for (Entry& e : reg) if (e.id == id) return e;
        throw std::out_of_range("немає рядка " + id);
    };
    find("P-02").plan("ключ ідемпотентності на платіж + нічна звірка з банком",
                      Rating(SEVERITY("закон"), OCCURRENCE("усунено"),
                             DETECTION("на-місці")));
    find("P-03").plan("скидати кеш подією переоцінки + монітор розбіжності ціни",
                      Rating(SEVERITY("прикро"), OCCURRENCE("1:10к"),
                             DETECTION("на-місці")));

    show("ПІСЛЯ ЗАХОДІВ:", by_priority(reg, /*before=*/false), /*before=*/false);
    std::cout << "\n";
    for (const Entry& e : by_priority(reg, /*before=*/true)) {
        if (!e.after) {
            std::cout << e.id << ": " << std::left << std::setw(7) << name(e.before.ap())
                      << "→ дій не заплановано, ризик прийнято свідомо\n";
            continue;
        }
        std::cout << e.id << ": " << std::left << std::setw(7) << name(e.before.ap())
                  << "→ " << std::setw(7) << name(e.after->ap())
                  << "RPN " << std::right << std::setw(3) << e.before.rpn() << " → "
                  << std::left << std::setw(3) << e.after->rpn()
                  << "  S " << e.before.s << "→" << e.after->s
                  << "   O " << e.before.o << "→" << e.after->o
                  << "   D " << e.before.d << "→" << e.after->d << "\n";
    }
    return 0;
}
