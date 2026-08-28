# Грубо — не означає «усе підряд». Список малює лише кімнату й стан.
@dataclass
class ListItemDTO:
    v: int; id: str; room: str; state: str

class Hub:
    # ... snapshot() лишається для екрана деталей ...
    def list_view(self):                     # той самий 1 перехід, утричі менший пакунок
        return [ListItemDTO(1, d.id, d.room(), d.state())
                for d in self._devices.values()]
