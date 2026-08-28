interface Mediator {
  notify(sender: Widget, event: string): void;   // єдине, що колега кличе
}

abstract class Widget {                           // КОЛЕГА
  constructor(protected mediator: Mediator) {}    // знає лише посередника
}

class Checkbox extends Widget {
  checked = false;
  toggle() {
    this.checked = !this.checked;
    this.mediator.notify(this, "toggled");        // «я змінився» — і все
  }
}

class TextField extends Widget {
  value = "";
  enabled = true;
  setValue(v: string) {
    this.value = v;
    this.mediator.notify(this, "typed");
  }
}

class Button extends Widget {
  enabled = false;
  render() { console.log(`[Оформити] ${this.enabled ? "активна" : "згасла"}`); }
}
