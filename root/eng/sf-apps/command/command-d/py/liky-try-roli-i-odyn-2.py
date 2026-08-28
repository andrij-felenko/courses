class ToolbarButton:
    def __init__(self, command: Command) -> None:
        self.command = command               # тримає абстрактну команду
    def on_click(self) -> None:
        self.command.execute()               # тисне ґудзик, і все

# збірка: тут — і тільки тут — вирішуємо, ЩО робить кнопка
doc = Document()
add_btn = ToolbarButton(AddText(doc, "привіт"))
del_btn = ToolbarButton(DeleteLast(doc))
