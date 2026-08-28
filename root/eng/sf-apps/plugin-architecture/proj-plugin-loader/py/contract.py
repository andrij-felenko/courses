# contract.py — це знають ОБИДВІ сторони: і ядро, і кожен автор плагіна.
# Номер версії контракту. Піднімаємо його ЩОРАЗУ, коли міняємо форму гнізда
# так, що старі плагіни перестають працювати (несумісна зміна).
HOST_API = 3

from typing import Protocol

class Exporter(Protocol):
    extension: str                                   # "pdf", "html", "md"
    def export(self, doc: "Document") -> bytes: ...  # документ -> байти

class Host(Protocol):
    """Вузьке вікно, яке ядро дає плагінові. НІЧОГО, крім цього, плагін
    про ядро не знає — і не може дотягтись до його нутрощів."""
    def register_exporter(self, e: Exporter) -> None: ...

# Умовлена точка входу. КОЖЕН плагін-файл зобов'язаний виставити саме її:
#     PLUGIN_API = 3
#     def register(host: Host) -> None: ...
