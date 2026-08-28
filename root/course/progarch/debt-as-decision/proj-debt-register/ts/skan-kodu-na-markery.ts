import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

const MARKER = /DEBT\((DH-\d+)\)/g;             // // DEBT(DH-014) — саме мітка, не слово
interface Marker { id: string; at: string; }

function walk(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = join(dir, e.name);
    return e.isDirectory() ? walk(p) : [p];
  });
}

function scanMarkers(root: string): Marker[] {
  const out: Marker[] = [];
  for (const file of walk(root)) {
    if (!/\.(ts|js|sql)$/.test(file)) continue;
    readFileSync(file, "utf8").split("\n").forEach((ln, i) => {
      for (const m of ln.matchAll(MARKER))
        out.push({ id: m[1], at: `${relative(root, file).replaceAll("\\", "/")}:${i + 1}` });
    });
  }
  return out;
}
