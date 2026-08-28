type DialogEvent =
  | { kind: "changed"; field: FieldId }               // значення оновилось
  | { kind: "toggled"; field: "shipSame" | "terms" }; // клацнути можна ЛИШЕ прапорці

interface Mediator { notify(e: DialogEvent): void; }

// у посереднику — розбір, який компілятор перевіряє на вичерпність:
notify(e: DialogEvent) {
  switch (e.field) {
    case "country":  this.region.setOptions(REGIONS[this.country.value] ?? []); break;
    case "shipSame": this.shipping.enabled = !this.shipSame.checked;
                     if (this.shipSame.checked) this.shipping.value = ""; break;
    case "promo":    this.discount = PROMO[this.promo.value.trim()] ?? 0; break;
    case "email": case "password": case "confirm":
    case "region": case "shipping": case "terms": break;   // лише ревалідація
    default: assertNever(e.field);   // забув гілку для нового поля → помилка КОМПІЛЯЦІЇ
  }
  this.revalidate();
}

function assertNever(x: never): never { throw new Error("незакрите поле: " + x); }
