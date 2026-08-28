abstract class Dialog {
  // фабричний метод: тип результату — АБСТРАКЦІЯ, конкретики каркас не знає
  protected abstract createButton(): Button;

  render(): void {                 // шаблонний метод — незмінний скелет
    const ok = this.createButton();   // ...кличе діру...
    ok.onClick(() => this.close());
    ok.paint();
  }
  close(): void { /* спільна логіка */ }
}

class WindowsDialog extends Dialog {
  // коваріантне звуження: повертаємо КОНКРЕТНІШИЙ тип, і це легально
  protected createButton(): WindowsButton {
    return new WindowsButton();
  }
}
