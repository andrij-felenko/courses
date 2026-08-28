class SearchService {
  private abortController: AbortController | null = null;

  public search = debounce(async (query: string) => {
    // Скасовуємо попередній незавершений мережевий запит
    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        signal: this.abortController.signal,
      });
      const data = await response.json();
      this.renderResults(data);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Помилка пошуку:', err);
      }
    }
  }, 300);

  private renderResults(data: any): void {
    // Оновлення списку результатів у DOM
  }
}
