// одна конфігурована фабрика замість класу-на-родину
class PrototypeFactory implements GuiFactory {
  constructor(private readonly protos: { button: Button; checkbox: Checkbox }) {}
  createButton(): Button     { return this.protos.button.clone(); }
  createCheckbox(): Checkbox { return this.protos.checkbox.clone(); }
}

// родина — це просто НАБІР ПРОТОТИПІВ; нова родина = новий набір, БЕЗ нового класу
const dark  = new PrototypeFactory({ button: darkButtonProto,  checkbox: darkCheckboxProto });
const light = new PrototypeFactory({ button: lightButtonProto, checkbox: lightCheckboxProto });
