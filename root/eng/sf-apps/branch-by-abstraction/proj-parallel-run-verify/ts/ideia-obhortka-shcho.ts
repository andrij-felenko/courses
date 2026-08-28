interface Renderer {
  render(template: string, data: Record<string, unknown>): string;
}

// Звіряч — сам реалізація шва, тримає стару (control) й нову (candidate)
class ComparingRenderer implements Renderer {
  constructor(
    private control: Renderer,      // стара, їй довіряємо — її вихід іде клієнтові
    private candidate: Renderer,    // нова, у тіні
    private log: MismatchLog,
  ) {}

  render(template: string, data: Record<string, unknown>): string {
    const result = this.control.render(template, data);   // це піде користувачеві

    // Нова — в тіні. Її помилка НЕ сміє зачепити користувача,
    // тож ловимо все, що вона кине, і трактуємо як розбіжність.
    try {
      const shadow = this.candidate.render(template, data);
      if (shadow !== result) {
        this.log.mismatch({ template, control: result, candidate: shadow });
      }
    } catch (err) {
      this.log.candidateThrew({ template, error: err });
    }

    return result;                  // завжди повертаємо перевірене
  }
}
