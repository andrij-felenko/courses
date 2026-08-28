// Потокове читання відповіді через Fetch API
async function fetchStreamedData(url: string, onChunk: (text: string) => void): Promise<void> {
  const response = await fetch(url, {
    headers: { "Accept": "text/plain; charset=utf-8" },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("Потік відповіді недоступний");

  const decoder = new TextDecoder("utf-8");
  let isDone = false;

  while (!isDone) {
    const { value, done } = await reader.read();
    if (done) {
      isDone = true;
      break;
    }
    // value є масивом Uint8Array; декодуємо байти у текст без блокування потоку UI
    const chunkText = decoder.decode(value, { stream: true });
    onChunk(chunkText);
  }
}
