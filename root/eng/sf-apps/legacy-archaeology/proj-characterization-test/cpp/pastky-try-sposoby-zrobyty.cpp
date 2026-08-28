// Порядок і час прибрали; лишилась третя міна — випадковий UUID у виводі.
// Лік: детермінований генератор під тестом (шов, як і для годинника).
struct IdGen { std::function<std::string()> next; };

std::string renderWithId(const Invoice& inv, IdGen& ids) {
    std::ostringstream os;
    os << "ID " << ids.next() << "\n";        // під тестом -> передбачувано
    os << renderInvoice(inv);
    return os.str();
}
// У тесті:
//   int n = 0;
//   IdGen ids{ [&]{ return "ID-" + std::to_string(++n); } };  // 1,2,3...
// У проді той самий IdGen отримує справжній генератор UUID.
