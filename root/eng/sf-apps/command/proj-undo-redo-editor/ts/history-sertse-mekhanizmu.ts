class History {
  private done: Command[] = [];      // виконані, ще не скасовані
  private undone: Command[] = [];    // скасовані, чекають на redo

  // виконати НОВУ дію
  run(cmd: Command): void {
    cmd.execute();
    this.done.push(cmd);
    this.undone.length = 0;          // ← інваріант: нова дія стирає redo-гілку
  }

  undo(): void {
    const cmd = this.done.pop();
    if (cmd === undefined) return;   // край: скасовувати нічого
    cmd.undo();
    this.undone.push(cmd);
  }

  redo(): void {
    const cmd = this.undone.pop();
    if (cmd === undefined) return;   // край: повторювати нічого
    cmd.execute();
    this.done.push(cmd);
  }

  canUndo(): boolean { return this.done.length > 0; }
  canRedo(): boolean { return this.undone.length > 0; }
}
