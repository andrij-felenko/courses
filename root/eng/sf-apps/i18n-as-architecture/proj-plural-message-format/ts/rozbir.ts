type Node =
  | { t: "text"; v: string }                       // дослівний шматок
  | { t: "arg"; name: string }                     // {folder}
  | { t: "hash" }                                  // # усередині гілки
  | { t: "choice"; name: string; kind: "plural" | "select";
      offset: number; branches: Record<string, Node[]> };

function parse(src: string): Node[] {
  let i = 0;
  const fail = (why: string): never => {
    throw new SyntaxError(`${why} — позиція ${i} у «${src}»`);
  };
  const ws = () => { while (i < src.length && /\s/.test(src[i])) i++; };
  const word = (): string => {
    const from = i;
    while (i < src.length && /[A-Za-z0-9_.=+-]/.test(src[i])) i++;
    return i > from ? src.slice(from, i) : fail("очікував ім'я або мітку");
  };

  // Текст із дірками. inBranch=true — спиняємось на '}' і розуміємо '#'.
  const body = (inBranch: boolean): Node[] => {
    const out: Node[] = [];
    let buf = "";
    const flush = () => { if (buf) { out.push({ t: "text", v: buf }); buf = ""; } };

    while (i < src.length) {
      const c = src[i];
      if (c === "}" && inBranch) break;
      if (c === "#" && inBranch) { flush(); out.push({ t: "hash" }); i++; continue; }
      if (c === "{") { flush(); out.push(hole()); continue; }
      if (c === "'") {                          // апостроф за правилом ICU 4.8+
        const next = src[i + 1];
        if (next === "'") { buf += "'"; i += 2; continue; }   // '' → один апостроф
        if (next && "{}#".includes(next)) {                   // '…' → дослівний текст
          i++;
          while (i < src.length && src[i] !== "'") buf += src[i++];
          i++;
          continue;
        }
        buf += "'"; i++; continue;               // звичайний апостроф: «п'ять»
      }
      buf += c; i++;
    }
    flush();
    return out;
  };

  const hole = (): Node => {
    i++; ws();                                             // з'їли '{'
    const name = word(); ws();
    if (src[i] === "}") { i++; return { t: "arg", name }; } // просте місце {folder}
    if (src[i] !== ",") fail("очікував ',' або '}'");
    i++; ws();
    const kind = word();
    if (kind !== "plural" && kind !== "select") fail(`невідомий різновид «${kind}»`);
    ws();
    if (src[i] !== ",") fail("очікував ',' після різновиду");
    i++; ws();
    let offset = 0;
    if (src.startsWith("offset:", i)) { i += "offset:".length; offset = Number(word()); ws(); }

    const branches: Record<string, Node[]> = {};
    while (i < src.length && src[i] !== "}") {
      const label = word(); ws();                          // one | few | =0 | female…
      if (src[i] !== "{") fail(`очікував '{' після мітки «${label}»`);
      i++;
      branches[label] = body(true);                        // гілка — теж повідомлення
      if (src[i] !== "}") fail(`незакрита гілка «${label}»`);
      i++; ws();
    }
    if (src[i] !== "}") fail("незакрите місце");
    i++;
    if (!branches.other) fail("гілка other обов'язкова");
    return { t: "choice", name, kind, offset, branches };
  };

  return body(false);
}
