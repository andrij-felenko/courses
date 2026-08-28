const doc = new TextDocument();
const h = new History();

h.run(new AddText(doc, 0, "привіт"));          // "привіт"
h.run(new AddText(doc, 6, " світе"));          // "привіт світе"
h.run(new DeleteLastWord(doc));                // "привіт "   (зрізали "світе")

h.undo();                                       // "привіт світе"  (повернули слово)
h.undo();                                       // "привіт"        (прибрали " світе")
h.redo();                                       // "привіт світе"  (повторили вставку)

h.run(new ReplaceRange(doc, 0, 6, "здоров"));  // "здоров світе"
// ↑ нова дія: стопка undone очищена — того, що було скасовано раніше, вже не повернути

console.log(doc.content());                     // "здоров світе"
console.log(h.canRedo());                        // false — redo-гілка стерта новою дією
