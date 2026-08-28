// контракт — простий носій даних (Transfer Object), без жодної поведінки
record UserRow(long id, String email, String role, boolean active) {}

// інтерфейс DAO — що з цими даними можна робити
interface UserDao {
    UserRow findById(long id);
    List<UserRow> findByRole(String role);
    void insert(UserRow u);
    void update(UserRow u);
    void delete(long id);
}

// бізнес-код залежить ЛИШЕ від інтерфейсу — жодного натяку на сховище
class ApprovalService {
    private final UserDao users;
    ApprovalService(UserDao users) { this.users = users; }

    List<String> approverEmails() {
        return users.findByRole("approver").stream()
            .filter(UserRow::active)
            .map(UserRow::email)
            .toList();
    }
}
