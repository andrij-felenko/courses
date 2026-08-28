@dataclass(frozen=True)
class RuleDTO:
    rule_id: str
    home_id: str
    name: str
    is_enabled: bool
    trigger_conditions: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    created_at: datetime
    last_triggered_at: datetime | None
