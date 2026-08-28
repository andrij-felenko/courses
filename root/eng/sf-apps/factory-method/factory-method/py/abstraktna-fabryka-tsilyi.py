from abc import ABC, abstractmethod

class UiFactory(ABC):                       # абстрактна фабрика: метод на КОЖЕН продукт
    @abstractmethod
    def create_button(self) -> "Button": ...
    @abstractmethod
    def create_checkbox(self) -> "Checkbox": ...
    @abstractmethod
    def create_input(self) -> "Input": ...

class DarkFactory(UiFactory):               # уся родина — темна
    def create_button(self):   return DarkButton()
    def create_checkbox(self): return DarkCheckbox()
    def create_input(self):    return DarkInput()

class LightFactory(UiFactory):              # уся родина — світла
    def create_button(self):   return LightButton()
    def create_checkbox(self): return LightCheckbox()
    def create_input(self):    return LightInput()

# клієнт бере ОДНУ фабрику й будує з неї весь екран — узгодженість гарантована
def build_login_form(ui: UiFactory) -> None:
    btn = ui.create_button()
    remember = ui.create_checkbox()
    login = ui.create_input()
    # ... усе з однієї теми, змішати неможливо ...
