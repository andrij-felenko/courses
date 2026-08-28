# ДО: один клас, поле source, розвилка у валідації, півполя None
class User:
    source: str
    stage: Optional[str]; tax_id: Optional[str]   # +40 полів
    def is_valid(self) -> bool:
        if self.source == "sales":
            return self.stage is not None and self.owner_id is not None
        return self.tax_id is not None

# ПІСЛЯ: два чисті світи + перекладач на межі
@dataclass(frozen=True)
class Lead:  ...   # stage, probability, owner_id — усі обов'язкові
@dataclass(frozen=True)
class Payer: ...   # tax_id, credit_limit, iban — усі обов'язкові
def lead_to_payer(lead: Lead, tax_id: str, iban: str) -> Payer: ...  # межа
# source більше немає. is_valid() більше немає. None-полів немає.
