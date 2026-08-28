// tools/renames.ts — старий шлях → теперішній, зібране з R-записів git
import { execFileSync } from 'node:child_process';

export function renameMap(): Map<string, string> {
  const raw = execFileSync('git', [
    'log', '--name-status', '-M', '--diff-filter=R', '--pretty=format:', '--reverse',
  ], { encoding: 'utf8', maxBuffer: 1 << 26 });

  const step = new Map<string, string>();          // одне перейменування
  for (const line of raw.split('\n')) {
    const m = /^R\d*\t(.+)\t(.+)$/.exec(line);     // рядок виду «R100  старий  новий»
    if (m) step.set(m[1], m[2]);
  }

  // стиснути ланцюжок a→b→c до a→c; seen рятує від циклу a→b→a
  const final = (p: string): string => {
    const seen = new Set<string>();
    while (step.has(p) && !seen.has(p)) { seen.add(p); p = step.get(p)!; }
    return p;
  };
  return new Map([...step.keys()].map(k => [k, final(k)]));
}

const renames = renameMap();
export const canon = (file: string): string => renames.get(file) ?? file;
