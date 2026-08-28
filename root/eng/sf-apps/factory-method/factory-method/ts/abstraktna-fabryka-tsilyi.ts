interface UiFactory {              // абстрактна фабрика: метод на КОЖЕН вид продукту
  createButton(): Button;
  createCheckbox(): Checkbox;
  createInput(): Input;
}

class DarkFactory implements UiFactory {   // уся родина — темна
  createButton(): Button   { return new DarkButton(); }
  createCheckbox(): Checkbox { return new DarkCheckbox(); }
  createInput(): Input     { return new DarkInput(); }
}
class LightFactory implements UiFactory {  // уся родина — світла
  createButton(): Button   { return new LightButton(); }
  createCheckbox(): Checkbox { return new LightCheckbox(); }
  createInput(): Input     { return new LightInput(); }
}

// клієнт бере ОДНУ фабрику й будує з неї весь екран — узгодженість гарантована
function buildLoginForm(ui: UiFactory) {
  const btn = ui.createButton();
  const remember = ui.createCheckbox();
  const login = ui.createInput();
  // ... усе з однієї теми, змішати неможливо ...
}
