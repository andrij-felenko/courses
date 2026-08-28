const response = await fetch("/api/stream", { signal: abortController.signal });

if (!response.ok) {
  throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
}

const reader = response.body?.getReader();
const decoder = new TextDecoder("utf-8");

while (reader) {
  const { value, done } = await reader.read();
  if (done) break;
  // value є типізованим масивом Uint8Array
  const chunkText = decoder.decode(value, { stream: true });
  processChunkIncremental(chunkText);
}
