from abc import ABC, abstractmethod

# (1) AbstractFactory — операція на КОЖЕН вид продукту
class GuiFactory(ABC):
    @abstractmethod
    def create_button(self) -> "Button": ...       # (3) AbstractProduct
    @abstractmethod
    def create_checkbox(self) -> "Checkbox": ...    # (3) AbstractProduct

# (2) ConcreteFactory — увесь набір в одному стилі
class DarkFactory(GuiFactory):
    def create_button(self) -> "Button":     return DarkButton()      # (4) ConcreteProduct
    def create_checkbox(self) -> "Checkbox": return DarkCheckbox()    # (4) ConcreteProduct

# (5) Client — бачить лише абстракції
def build_form(ui: GuiFactory) -> list["Control"]:
    return [ui.create_button(), ui.create_checkbox()]
