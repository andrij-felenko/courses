class System {
  constructor(private truth: Truth, private read: Read) {}
  send(cmd: Command): void {
    const e = this.truth.handle(cmd);   // 1. записали правду
    this.read.notify(e);                // 2. повідомили читацький бік
  }
  view(): DashRow { return this.read.dashboard(this.truth); }
}

// ── ЧОТИРИ системи — вільна композиція двох осей, по рядку на кут ──
const plainCrud = new System(new CrudTruth(),  new FoldOnRead());  // ✗ ✗  дефолт
const crudCqrs  = new System(new CrudTruth(),  new Projection());  // ✗ ✓  CRUD + CQRS
const esSingle  = new System(new EventTruth(), new FoldOnRead());  // ✓ ✗  ES, одна модель
const esCqrs    = new System(new EventTruth(), new Projection());  // ✓ ✓  ES + CQRS
