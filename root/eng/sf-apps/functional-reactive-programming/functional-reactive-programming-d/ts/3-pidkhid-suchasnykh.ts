import { createSignal, createResource } from "solid-js";

const [query, setQuery] = createSignal("");

// createResource автоматично керує станом завантаження, скасуванням та кешуванням
const [results] = createResource(query, async (q) => {
  if (!q.trim()) return [];
  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  return res.json();
});

// У JSX/шаблоні:
// <input onInput={(e) => debounce(() => setQuery(e.target.value), 300)} />
// <Show when={results.loading}><Loader /></Show>
// <For each={results()}>{item => <ResultCard data={item} />}</For>
