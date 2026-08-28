let currentAbortController: AbortController | null = null;

async function updateStatus(newStatus: boolean) {
  // 1. Скасовуємо попередній запит у польоті
  if (currentAbortController) {
    currentAbortController.abort();
  }
  currentAbortController = new AbortController();

  // 2. Оптимістично оновлюємо UI
  setOptimisticStatus(newStatus);

  try {
    const response = await fetch('/api/status', {
      method: 'POST',
      body: JSON.stringify({ status: newStatus }),
      signal: currentAbortController.signal // прив'язка сигналу скасування
    });
    const data = await response.json();
    setCanonicalStatus(data.status);
  } catch (err: any) {
    if (err.name === 'AbortError') {
      // Запит було правомірно перервано новішою дією — нічого не відкочуємо!
      return;
    }
    // Справжній збій мережі — виконуємо відкат
    rollbackStatus();
  }
}
