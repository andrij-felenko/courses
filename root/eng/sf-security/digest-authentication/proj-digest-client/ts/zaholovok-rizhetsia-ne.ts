import { createHash, createHmac, randomBytes, timingSafeEqual } from 'node:crypto';

const ITEM =
  /\s*(?:,\s*)*([A-Za-z][A-Za-z0-9_.-]*)(?:\s*=\s*(?:"((?:[^"\\]|\\.)*)"|([^\s,]*)))?/y;

export type Challenge = { scheme: string; params: Record<string, string> };

/** Заголовок → потік [ім'я, значення]. Значення null ⇒ це назва схеми. */
function* items(header: string): Generator<[string, string | null]> {
  ITEM.lastIndex = 0;
  for (let m = ITEM.exec(header); m !== null; m = ITEM.exec(header)) {
    const [, key, quoted, token] = m;
    const value =
      quoted !== undefined ? quoted.replace(/\\(.)/g, '$1')  // кома в лапках — не роздільник
      : token !== undefined ? token
      : null;
    yield [key.toLowerCase(), value];
  }
}

/** WWW-Authenticate → виклики в тому порядку, як їх дала служба. */
export function parseChallenges(header: string): Challenge[] {
  const out: Challenge[] = [];
  for (const [key, value] of items(header)) {
    if (value === null) out.push({ scheme: key, params: {} }); // слово без «=» → нова схема
    else if (out.length) out[out.length - 1].params[key] = value;
  }
  return out;
}

/** Authentication-Info і подібні — самі поля, без назви схеми. */
export const parseParams = (header: string): Record<string, string> =>
  Object.fromEntries([...items(header)].filter((e): e is [string, string] => e[1] !== null));

const ALGORITHMS: Record<string, { hash: string; strength: number }> = {
  'SHA-512-256': { hash: 'sha512-256', strength: 3 },  // SHA-512/256 з FIPS 180-4,
  'SHA-256':     { hash: 'sha256',     strength: 2 },  // а НЕ обрізаний sha512
  'MD5':         { hash: 'md5',        strength: 1 },
};

const splitAlg = (name: string) => {
  const sess = name.toUpperCase().endsWith('-SESS');
  return { base: (sess ? name.slice(0, -5) : name).toUpperCase(), sess };
};

/** Найсильніший Digest-виклик із тих, що ми вміємо: порядок у заголовку не захищений. */
export function pick(challenges: Challenge[]): Challenge | null {
  let best: Challenge | null = null, bestStrength = 0;
  for (const ch of challenges) {
    if (ch.scheme !== 'digest') continue;
    const known = ALGORITHMS[splitAlg(ch.params.algorithm ?? 'MD5').base];
    if (known && known.strength > bestStrength) { best = ch; bestStrength = known.strength; }
  }
  return best;
}
