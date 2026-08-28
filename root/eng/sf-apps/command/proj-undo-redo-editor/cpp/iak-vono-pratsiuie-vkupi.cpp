TextDocument doc;
History h;

h.run(std::make_unique<AddText>(doc, 0, "привіт"));             // "привіт"
h.run(std::make_unique<AddText>(doc, doc.length(), " світе"));  // "привіт світе"
h.run(std::make_unique<DeleteLastWord>(doc));                   // "привіт "   (зрізали "світе")

h.undo();                                                       // "привіт світе"  (повернули слово)
h.undo();                                                       // "привіт"        (прибрали " світе")
h.redo();                                                       // "привіт світе"  (повторили вставку)

// нова дія: замінюємо перше слово; [0, 12) — байти "привіт" в UTF-8
h.run(std::make_unique<ReplaceRange>(doc, 0, 12, "здоров"));    // "здоров світе"
// ↑ стопка undone очищена — того, що було скасовано раніше, вже не повернути

std::cout << doc.content() << '\n';                 // "здоров світе"
std::cout << std::boolalpha << h.canRedo() << '\n'; // false — redo-гілку стерто новою дією
