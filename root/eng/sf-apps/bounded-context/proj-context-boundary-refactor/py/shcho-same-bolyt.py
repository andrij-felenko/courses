# Один User на всю систему — і продажам, і бухгалтерії
from typing import Optional, Literal

class User:
    def __init__(self) -> None:
        self.id: str = ""
        self.name: str = ""
        self.email: str = ""

        # маркер, «звідки» цей юзер — уже симптом
        self.source: Literal["sales", "billing"] = "sales"

        # поля продажів (для бухгалтерського юзера — None)
        self.stage: Optional[str] = None       # new | qualified | won | lost
        self.probability: Optional[float] = None   # 0..1, шанс закрити
        self.owner_id: Optional[str] = None    # менеджер, що веде

        # поля бухгалтерії (для продажного юзера — None)
        self.tax_id: Optional[str] = None      # ІПН / ЄДРПОУ
        self.credit_limit: Optional[float] = None
        self.iban: Optional[str] = None

        # ...ще три десятки полів, половина завжди None

    def is_valid(self) -> bool:
        if self.source == "sales":
            # продажний юзер валідний, якщо має стадію й менеджера
            return self.stage is not None and self.owner_id is not None
        # бухгалтерський — якщо має ІПН
        return self.tax_id is not None
