export type Selection = { nodeId: string; from: number; to: number };

export type EditResult = {
  root: Node;
  removed: number;        // байти, що пішли з дерева
  dropped: Node[];        // вилучені носії ресурсів — помруть із кроком на дні
  added: Node[];          // додані носії ресурсів — помруть, коли зріжуть гілку повтору
};
export type Edit = (root: Node) => EditResult;

export type Step = {
  before: Node; after: Node;
  selBefore: Selection; selAfter: Selection;
  label: string; mergeKey: string;
  weight: number;
  dropped: Node[]; added: Node[];
  at: number;
};

export class Store {
  private root: Node;                       // ← єдина змінна комірка
  private sel: Selection = { nodeId: "", from: 0, to: 0 };
  private steps: Step[] = [];
  private index = 0;                        // курсор на лінії історії
  private saved = 0;                        // −1 ⇒ збережений стан недосяжний
  private bytes = 0;
  private open: {
    base: Node; selBefore: Selection; label: string; mergeKey: string;
    born0: number; removed: number; dropped: Node[]; added: Node[];
  } | null = null;

  constructor(root: Node,
              private budget: number,
              private notify: () => void) { this.root = root; }

  doc(): Node { return this.root; }
  selection(): Selection { return this.sel; }
  markSaved(): void { this.saved = this.index; }
  isDirty(): boolean { return this.saved !== this.index; }
}
