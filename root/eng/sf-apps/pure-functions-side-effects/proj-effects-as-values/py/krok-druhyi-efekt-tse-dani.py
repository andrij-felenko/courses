from dataclasses import dataclass

# кожен варіант — свій незмінний клас; Effect — їх об'єднання
@dataclass(frozen=True)
class SaveUser:     user: "User"
@dataclass(frozen=True)
class AppendLedger: user_id: int; amount: int; at: int
@dataclass(frozen=True)
class Notify:       to: str; text: str

Effect = SaveUser | AppendLedger | Notify
