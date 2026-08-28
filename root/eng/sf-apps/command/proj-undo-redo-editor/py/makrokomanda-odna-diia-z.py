class MacroCommand:
    def __init__(self, commands: list[Command]) -> None:
        self.commands = commands

    def execute(self) -> None:
        for c in self.commands:          # усі вперед, по порядку
            c.execute()

    def undo(self) -> None:
        for c in reversed(self.commands):  # ...і назад у ЗВОРОТНОМУ
            c.undo()
