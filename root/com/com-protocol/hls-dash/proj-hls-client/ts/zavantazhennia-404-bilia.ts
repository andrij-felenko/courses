type Fetched = ArrayBuffer | 'wait' | 'skip';

let ewma = 0;                 // Мбіт/с — згладжена оцінка швидкості
const ALPHA = 0.4;            // вага свіжого виміру

async function fetchSegment(seg: Segment, atEdge: boolean): Promise<Fetched> {
  for (let attempt = 0; attempt < 3; attempt++) {
    const t0 = performance.now();          // засікаємо ДО запиту, а не з першого байта
    const res = await fetch(seg.url.href);

    if (res.ok) {
      const bytes = await res.arrayBuffer();
      const secs = (performance.now() - t0) / 1000;
      const mbps = (bytes.byteLength * 8) / 1e6 / secs;
      ewma = ewma === 0 ? mbps : ALPHA * mbps + (1 - ALPHA) * ewma;
      return bytes;
    }
    if (res.status === 404 && atEdge) return 'wait';   // оголошений раніше, ніж доїхав
    await sleep(200 * (attempt + 1));                  // вузол роздачі промазав — пробуємо ще
  }
  return atEdge ? 'wait' : 'skip';                     // у глибині вікна його вже нема
}
