// контракт — простий носій даних, без жодної поведінки
type UserRow = { id: number; email: string; role: string; active: boolean };

// інтерфейс DAO — що з цими даними можна робити
interface UserDao {
  findById(id: number): Promise<UserRow | null>;
  findByRole(role: string): Promise<UserRow[]>;
  insert(u: UserRow): Promise<void>;
  update(u: UserRow): Promise<void>;
  delete(id: number): Promise<void>;
}

// бізнес-код залежить ЛИШЕ від інтерфейсу — жодного натяку на сховище
class ApprovalService {
  constructor(private users: UserDao) {}

  async approverEmails(): Promise<string[]> {
    const rows = await this.users.findByRole("approver");
    return rows.filter(u => u.active).map(u => u.email);
  }
}
