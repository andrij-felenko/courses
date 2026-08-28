class Email {
  private constructor(readonly value: string) {}   // конструктор закритий

  // єдиний вхід — через фабрику, що перевіряє
  static create(raw: string): Email {
    const normalized = raw.trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(normalized))
      throw new Error(`не email: ${raw}`);
    return new Email(normalized);
  }

  equals(other: Email): boolean { return this.value === other.value; }
}

// Далі по всій системі тип Email — це ГАРАНТІЯ, а не надія:
function sendWelcome(to: Email) {
  // тут НЕ треба перевіряти — якщо в руках Email, він уже валідний і нормалізований
}

Email.create("  Ivan@Example.COM ");   // ок → зберігає "ivan@example.com"
Email.create("привіт");                 // кине помилку тут-таки, а не колись потім
