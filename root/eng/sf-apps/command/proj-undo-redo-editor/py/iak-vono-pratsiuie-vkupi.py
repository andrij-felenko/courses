doc = TextDocument()
h = History()

h.run(AddText(doc, 0, "привіт"))            # "привіт"
h.run(AddText(doc, 6, " світе"))            # "привіт світе"
h.run(DeleteLastWord(doc))                  # "привіт "   (зрізали "світе")

h.undo()                                    # "привіт світе"  (повернули слово)
h.undo()                                    # "привіт"        (прибрали " світе")
h.redo()                                    # "привіт світе"  (повторили вставку)

h.run(ReplaceRange(doc, 0, 6, "здоров"))    # "здоров світе"
# ↑ нова дія: стопка undone очищена — того, що було скасовано раніше, вже не повернути

print(doc.content())                        # "здоров світе"
print(h.can_redo())                         # False — redo-гілка стерта новою дією
