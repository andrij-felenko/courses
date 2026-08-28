interface Flags {
  // Детермінований відсоток: той самий ключ+ідентифікатор → та сама відповідь,
  // тож один користувач стабільно або в тіні, або ні — не мерехтить від виклику до виклику.
  sampled(key: string, id: string): boolean;
}

class ComparingRenderer implements Renderer {
  constructor(
    private control: Renderer,
    private candidate: Renderer,
    private log: MismatchLog,
    private flags: Flags,
  ) {}

  render(template: string, data: Record<string, unknown>): string {
    const result = this.control.render(template, data);

    // У тінь потрапляє лише вибрана відсотком частка викликів
    if (this.flags.sampled("render-shadow-percent", template)) {
      const started = performance.now();
      try {
        const shadow = this.candidate.render(template, data);
        this.log.timing("candidate", performance.now() - started);   // вартість
        if (shadow !== result) {
          this.log.mismatch({ template, control: result, candidate: shadow });
        }
      } catch (err) {
        this.log.candidateThrew({ template, error: err });
      }
    }
    return result;
  }
}
