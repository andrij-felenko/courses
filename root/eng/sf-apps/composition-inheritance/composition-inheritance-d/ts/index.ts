interface Clock { now(): number; }

class Order {
    constructor(private clock: Clock) {}          // залежність ПРИЙНЯТО ззовні
    stamp(): number { return this.clock.now(); }
}

// у тесті підставляємо фальшивий годинник — час стає передбачуваним
const fake: Clock = { now: () => 1_000 };
new Order(fake).stamp();                          // рівно 1000, тест детермінований
