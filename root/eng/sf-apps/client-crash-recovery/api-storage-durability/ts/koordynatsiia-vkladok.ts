// Запит ексклюзивного права на модифікацію документа
await navigator.locks.request(
  `doc-lock-${documentId}`,
  { mode: "exclusive", ifAvailable: true },
  async (lock) => {
    if (!lock) {
      // Інша вкладка вже редагує документ
      console.warn("Документ заблоковано іншим сеансом. Перехід у режим Read-Only.");
      return;
    }
    // Ексклюзивне володіння: виконуємо запис у WAL
    await runDocumentEventLoop();
  }
);
