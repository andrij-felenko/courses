class InMemoryUsers:                                  # ФЕЙК
    def __init__(self) -> None:
        self._rows: dict[str, User] = {}

    async def find_by_email(self, email: str) -> "User | None":
        return self._rows.get(email)

    async def save(self, user: User) -> None:
        self._rows[user.email] = user                 # тихо перезапише

async def register(email: str, users: Users) -> User:
    if await users.find_by_email(email):
        raise EmailTaken(email)
    user = User(id=new_id(), email=email)
    await users.save(user)                            # між перевіркою і записом — вікно
    return user
