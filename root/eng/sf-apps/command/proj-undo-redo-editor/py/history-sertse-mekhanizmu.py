class History:
    def __init__(self) -> None:
        self._done: list[Command] = []     # виконані, ще не скасовані
        self._undone: list[Command] = []   # скасовані, чекають на redo

    # виконати НОВУ дію
    def run(self, cmd: Command) -> None:
        cmd.execute()
        self._done.append(cmd)
        self._undone.clear()               # ← інваріант: нова дія стирає redo-гілку

    def undo(self) -> None:
        if not self._done:                 # край: скасовувати нічого
            return
        cmd = self._done.pop()
        cmd.undo()
        self._undone.append(cmd)

    def redo(self) -> None:
        if not self._undone:               # край: повторювати нічого
            return
        cmd = self._undone.pop()
        cmd.execute()
        self._done.append(cmd)

    def can_undo(self) -> bool: return len(self._done) > 0
    def can_redo(self) -> bool: return len(self._undone) > 0
