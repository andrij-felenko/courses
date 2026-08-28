class AutocompleteController {
  abortController = null;

  onInputChanged = debounce(async (query) => {
    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();

    try {
      const response = await fetch(`/api/suggest?q=${encodeURIComponent(query)}`, {
        signal: this.abortController.signal,
      });
      const suggestions = await response.json();
      this.renderDropdown(suggestions);
    } catch (err) {
      if (err.name !== 'AbortError') {
        this.showErrorState(err);
      }
    }
  }, 300);

  renderDropdown(items) {
    // Оновлення списку підказок у DOM
  }

  showErrorState(err) {
    // Відображення стану помилки
  }
}
