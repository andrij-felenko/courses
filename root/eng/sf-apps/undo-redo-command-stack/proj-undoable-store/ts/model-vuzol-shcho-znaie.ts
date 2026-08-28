type Res = { release(): void };          // зовнішній ресурс: Blob URL, текстура, файл

type Node = Readonly<{
  id: string;                            // стабільний; переживає всі версії документа
  text: string;
  kids: readonly Node[];
  own: number;                           // вага самого вузла
  bytes: number;                         // вага піддерева
  res?: Res;
}>;

let born = 0;                            // оцінка народжених байтів, не бухгалтерія

export function mk(id: string, text: string,
                   kids: readonly Node[] = [], res?: Res): Node {
  const own = 72 + 2 * (id.length + text.length) + 8 * kids.length;  // рядки в UTF-16
  born += own;
  return Object.freeze({                 // freeze робить незмінність помилкою, а не домовленістю
    id, text, kids, own, res,
    bytes: own + kids.reduce((s, k) => s + k.bytes, 0),
  });
}

export function replaceById(n: Node, id: string, repl: Node): Node {
  if (n.id === id) return repl;
  for (let i = 0; i < n.kids.length; i++) {
    const nk = replaceById(n.kids[i], id, repl);
    if (nk !== n.kids[i]) {               // ціль знайшлася в цій гілці
      const kids = n.kids.slice();        // копія масиву ПОСИЛАНЬ, не піддерев
      kids[i] = nk;
      return mk(n.id, n.text, kids);
    }
  }
  return n;                               // тут цілі немає — вузол лишається спільним
}

export function removeById(n: Node, id: string): { root: Node; removed: number; dropped: Node[] } {
  for (let i = 0; i < n.kids.length; i++) {
    if (n.kids[i].id === id) {
      const kids = n.kids.slice();
      const [gone] = kids.splice(i, 1);
      // dropped збираємо тільки з вузлів із зовнішнім ресурсом — саме їх доведеться
      // віддавати руками, бо збирач сміття цього не зробить
      return { root: mk(n.id, n.text, kids), removed: gone.bytes, dropped: withRes(gone) };
    }
    const r = removeById(n.kids[i], id);
    if (r.root !== n.kids[i]) {
      const kids = n.kids.slice();
      kids[i] = r.root;
      return { root: mk(n.id, n.text, kids), removed: r.removed, dropped: r.dropped };
    }
  }
  return { root: n, removed: 0, dropped: [] };
}

function withRes(n: Node, out: Node[] = []): Node[] {
  if (n.res) out.push(n);
  for (const k of n.kids) withRes(k, out);
  return out;
}
