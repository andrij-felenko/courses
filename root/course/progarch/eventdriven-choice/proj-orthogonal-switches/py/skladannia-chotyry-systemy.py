class System:
    def __init__(self, truth: Truth, read: Read):
        self.truth, self.read = truth, read
    def send(self, cmd: Command) -> None:
        e = self.truth.handle(cmd)     # 1. записали правду
        self.read.notify(e)            # 2. повідомили читацький бік
    def view(self) -> DashRow:
        return self.read.dashboard(self.truth)

# ── ЧОТИРИ системи — вільна композиція двох осей ──
plain_crud = System(CrudTruth(),  FoldOnRead())   # ✗ ✗  дефолт
crud_cqrs  = System(CrudTruth(),  Projection())   # ✗ ✓  CRUD + CQRS
es_single  = System(EventTruth(), FoldOnRead())   # ✓ ✗  ES, одна модель
es_cqrs    = System(EventTruth(), Projection())   # ✓ ✓  ES + CQRS
