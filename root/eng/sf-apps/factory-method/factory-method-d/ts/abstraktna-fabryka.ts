// (1) AbstractFactory — інтерфейс із операцією на КОЖЕН вид продукту
interface GuiFactory {
  createButton(): Button;      // (3) AbstractProduct «Button»
  createCheckbox(): Checkbox;  // (3) AbstractProduct «Checkbox»
}

// (2) ConcreteFactory — реалізує весь набір в одному стилі (зазвичай сінглтон)
class DarkFactory implements GuiFactory {
  createButton(): Button     { return new DarkButton(); }    // (4) ConcreteProduct
  createCheckbox(): Checkbox { return new DarkCheckbox(); }  // (4) ConcreteProduct
}

// (5) Client — бачить ЛИШЕ AbstractFactory та AbstractProduct, конкретних імен не знає
function buildForm(ui: GuiFactory): Control[] {
  return [ui.createButton(), ui.createCheckbox()];
}
