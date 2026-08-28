let timerId: number | null = null;
let lastRequestId = 0;
let isLoading = false;
let results = [];

inputElement.addEventListener("input", (e) => {
  const query = (e.target as HTMLInputElement).value.trim();
  if (!query) {
    results = [];
    renderResults([]);
    return;
  }

  if (timerId !== null) clearTimeout(timerId);

  timerId = window.setTimeout(() => {
    isLoading = true;
    renderLoader(true);
    const currentRequestId = ++lastRequestId;

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
      .then((res) => res.json())
      .then((data) => {
        // Захист від стану гонитви вручну через лічильник ID
        if (currentRequestId === lastRequestId) {
          results = data;
          renderResults(data);
        }
      })
      .catch((err) => handleError(err))
      .finally(() => {
        if (currentRequestId === lastRequestId) {
          isLoading = false;
          renderLoader(false);
        }
      });
  }, 300);
});
