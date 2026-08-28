let latestRequestId = 0;

async function handleSearchInput(query: string): Promise<void> {
  const currentRequestId = ++latestRequestId;
  showLoadingIndicator();

  try {
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await response.json();

    // Якщо за час польоту запиту користувач надіслав новіший запит — ігноруємо стару відповідь
    if (currentRequestId !== latestRequestId) {
      return;
    }

    renderSearchResults(data);
  } finally {
    if (currentRequestId === latestRequestId) {
      hideLoadingIndicator();
    }
  }
}
