let activeAbortController: AbortController | null = null;

async function handleSearchWithAbort(query: string): Promise<void> {
  // Скасовуємо попередній активний запит, якщо він ще в дорозі
  if (activeAbortController) {
    activeAbortController.abort();
  }

  activeAbortController = new AbortController();
  const { signal } = activeAbortController;

  try {
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, { signal });
    const data = await response.json();
    renderSearchResults(data);
  } catch (err: any) {
    if (err.name === "AbortError") {
      // Скасування є штатною ситуацією — тиша в логах
      return;
    }
    showErrorToast(err.message);
  }
}
