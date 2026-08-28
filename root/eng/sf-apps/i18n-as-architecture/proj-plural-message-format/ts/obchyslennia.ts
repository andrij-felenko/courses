type NumOpts = Intl.NumberFormatOptions & { type?: "cardinal" | "ordinal" };

const memo = <T,>(cache: Map<string, T>, key: string, make: () => T): T => {
  let v = cache.get(key);
  if (v === undefined) { v = make(); cache.set(key, v); }
  return v;
};
const nfs = new Map<string, Intl.NumberFormat>();
const prs = new Map<string, Intl.PluralRules>();

// ОДИН набір опцій живить і форматувальник чисел, і вибір форми:
// операнд v (скільки видимих десяткових) мусить збігтися в обох.
const nf = (loc: string, o: NumOpts) =>
  memo(nfs, loc + JSON.stringify(o), () => new Intl.NumberFormat(loc, o));
const pr = (loc: string, o: NumOpts) =>
  memo(prs, loc + JSON.stringify(o), () => new Intl.PluralRules(loc, o));

function run(nodes: Node[], args: Record<string, unknown>,
             loc: string, o: NumOpts, hash: string | null): string {
  let out = "";
  for (const n of nodes) {
    if (n.t === "text") { out += n.v; continue; }
    if (n.t === "hash") { out += hash ?? ""; continue; }
    if (n.t === "arg") {
      const v = args[n.name];
      out += typeof v === "number" ? nf(loc, o).format(v) : String(v);
      continue;
    }
    const v = args[n.name];
    let label: string;
    let inner = hash;
    if (n.kind === "plural") {
      const num = Number(v);
      const shown = num - n.offset;              // offset діє на форму й на '#'
      label = `=${num}` in n.branches            // точний збіг — за ПОВНИМ числом
        ? `=${num}`
        : pr(loc, o).select(shown);              // інакше — категорія від локалі
      inner = nf(loc, o).format(shown);
    } else {
      label = String(v) in n.branches ? String(v) : "other";
    }
    out += run(n.branches[label] ?? n.branches.other, args, loc, o, inner);
  }
  return out;
}
