class AutocompleteController {
  private abortController: AbortController | null = null;

  // Дебаунс на 300 мс для запобігання зайвим мережевим викликам
  public onInputChanged = debounce(async (query: string) => {
    // Скасовуємо попередній HTTP-запит, якщо він ще не завершився
    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();

    try {
      const response = await fetch(`/api/suggest?q=${encodeURIComponent(query)}`, {
        signal: this.abortController.signal,
      });
      const suggestions: string[] = await response.json();
      this.renderDropdown(suggestions);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        this.showErrorState(err);
      }
    }
  }, 300);

  private renderDropdown(items: string[]): void {
    // Оновлення списку підказок у DOM
  }

  private showErrorState(err: Error): void {
    // Відображення стану помилки
  }
}
