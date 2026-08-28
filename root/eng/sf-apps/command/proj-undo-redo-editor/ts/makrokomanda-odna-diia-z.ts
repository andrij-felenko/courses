class MacroCommand implements Command {
  constructor(private commands: Command[]) {}

  execute(): void {
    for (const c of this.commands) c.execute();          // усі вперед, по порядку
  }

  undo(): void {
    for (let i = this.commands.length - 1; i >= 0; i--)  // ...і назад у ЗВОРОТНОМУ
      this.commands[i].undo();
  }
}
