const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));
const MAX_BUFFER = 30;                    // секунд наперед — більше качати нема сенсу

async function play(masterUrl: URL,
                    sink: (s: Segment, bytes: ArrayBuffer) => void,
                    buffered: () => number) {   // секунд у буфері; у браузері це дає медіаелемент
  const top = await fetch(masterUrl.href);
  const variants = parseMultivariant(await top.text(), new URL(top.url));

  let level = 0;        // стартуємо з найдешевшої копії: першого виміру ще нізвідки взяти
  let next = -1;        // абсолютний номер сегмента, потрібного наступним
  let seen = '';        // тіло попереднього плейлиста — щоб побачити, що нового нема

  for (;;) {
    const res = await fetch(variants[level].url.href, { cache: 'no-store' });
    const body = await res.text();
    const pl = parseMedia(body, new URL(res.url));   // база — КІНЦЕВА адреса після переспрямувань
    const fresh = body !== seen;
    seen = body;

    const firstSeq = pl.mediaSequence;
    const lastSeq = firstSeq + pl.segments.length - 1;

    if (next < 0) next = Math.max(firstSeq, lastSeq - 2);   // три тривалості від кінця
    else if (next < firstSeq) {
      console.warn(`вікно поїхало: пропущено ${firstSeq - next} сегментів`);
      next = firstSeq;                                       // діру визнали, далі йдемо суцільно
    }

    while (next <= lastSeq && buffered() < MAX_BUFFER) {
      const seg = pl.segments[next - firstSeq];
      const got = await fetchSegment(seg, next === lastSeq);
      if (got === 'wait') break;                  // ще не доїхав — прийдемо по нього наступного разу
      if (got !== 'skip') sink(seg, got);
      next++;

      const want = choose(variants, level, ewma, buffered());
      if (want !== level) { level = want; seen = ''; break; }  // інший плейлист — звірку тіл скидаємо
    }

    if (pl.ended && next > lastSeq) return;
    await sleep(1000 * pl.targetDuration * (fresh ? 1 : 0.5));
  }
}
