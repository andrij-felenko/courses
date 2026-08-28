const orc = {
  hp: 10,
  attack() { return `б'є на ${this.hp}`; }
};

// boss НЕ копіює orc — він на нього ПОСИЛАЄТЬСЯ
const boss = Object.create(orc);
boss.hp = 40;

boss.attack();        // «б'є на 40» — метод узято з orc наживо, крізь посилання
orc.attack = function () { return "нова атака"; };   // міняємо сам ПРОТОТИП...
boss.attack();        // «нова атака» — boss бачить зміну, бо зв'язок живий
