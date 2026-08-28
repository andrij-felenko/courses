type FieldId =
  | "email" | "password" | "confirm" | "country" | "region"
  | "shipSame" | "shipping" | "promo" | "terms";

interface Mediator {
  notify(sender: FieldId, event: string): void;   // НАЇВНО: подія — рядок
}

class Field {                          // текстове поле-колега
  value = ""; enabled = true; error = "";
  constructor(readonly id: FieldId, private m: Mediator) {}
  setValue(v: string) { this.value = v; this.m.notify(this.id, "changed"); }
}

class Check {                          // прапорець-колега
  checked = false;
  constructor(readonly id: FieldId, private m: Mediator) {}
  toggle() { this.checked = !this.checked; this.m.notify(this.id, "toggled"); }
}

class Select extends Field {           // список — поле плюс набір варіантів
  options: string[] = [];
  setOptions(o: string[]) {
    this.options = o;
    if (!o.includes(this.value)) this.value = "";   // старий вибір більше не чинний
  }
}
