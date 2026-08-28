import { EventEmitter } from "node:events";

async function* streamToIterable<T>(
  src: EventEmitter,
  dataEvent = "data",
  endEvent = "end",
): AsyncGenerator<T> {
  const queue: T[] = [];
  let done = false;
  let failure: unknown = null;
  let wake: (() => void) | null = null;
  const bump = () => { wake?.(); wake = null; };

  const onData = (v: T) => { queue.push(v); bump(); };
  const onEnd = () => { done = true; bump(); };
  const onErr = (e: unknown) => { failure = e; done = true; bump(); };

  src.on(dataEvent, onData);
  src.once(endEvent, onEnd);
  src.once("error", onErr);       // 'error' БЕЗ слухача кладе процес — мусимо перехопити

  try {
    while (true) {
      while (queue.length) yield queue.shift()!;      // віддати все накопичене
      if (failure) throw failure;
      if (done) return;
      await new Promise<void>((r) => (wake = r));      // поспати до наступної події
    }
  } finally {
    src.off(dataEvent, onData);   // прибрати ВСІ слухачі —
    src.off(endEvent, onEnd);     // finally спрацює й на break споживача,
    src.off("error", onErr);      // і на throw в тілі, і на нормальний кінець
  }
}

// споживання читається як звичайний цикл:
for await (const chunk of streamToIterable<Buffer>(socket)) {
  handle(chunk);
  if (enough) break;   // ← generator.return() → спрацьовує finally → слухачі зняті
}
