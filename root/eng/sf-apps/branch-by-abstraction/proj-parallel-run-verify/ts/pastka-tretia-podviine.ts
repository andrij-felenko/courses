render(template: string, data: Record<string, unknown>): string {
  const result = this.control.render(template, data);   // користувач отримує ЦЕ негайно

  if (this.flags.sampled("render-shadow-percent", template)) {
    // Нова доганяє в тіні поза гарячим шляхом — латентності користувачеві не додає.
    queueMicrotask(() => {
      try {
        const shadow = this.candidate.render(template, data);
        if (shadow !== result) this.log.mismatch({ template, control: result, candidate: shadow });
      } catch (err) {
        this.log.candidateThrew({ template, error: err });
      }
    });
  }
  return result;   // не чекаємо на тінь
}
