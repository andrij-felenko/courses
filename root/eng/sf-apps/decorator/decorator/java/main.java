// КОМПОНЕНТ — спільний інтерфейс напою
interface Beverage {
    int cost();
    String description();
}

// КОНКРЕТНИЙ КОМПОНЕНТ — проста кава, яку обгортатимемо
class Coffee implements Beverage {
    public int cost()           { return 20; }
    public String description() { return "кава"; }
}

// БАЗОВИЙ ДЕКОРАТОР — тримає компонент і за замовчуванням просто ДЕЛЕГУЄ
abstract class AddOn implements Beverage {
    protected final Beverage inner;      // посилання типу КОМПОНЕНТА, не Coffee!
    protected AddOn(Beverage inner) { this.inner = inner; }
    public int cost()           { return inner.cost(); }         // просто передав
    public String description() { return inner.description(); }  // просто передав
}

// КОНКРЕТНІ ДЕКОРАТОРИ — навколо делегації додають своє
class Milk extends AddOn {
    Milk(Beverage inner) { super(inner); }
    public int cost()           { return inner.cost() + 5; }
    public String description() { return inner.description() + " + молоко"; }
}
class Cinnamon extends AddOn {
    Cinnamon(Beverage inner) { super(inner); }
    public int cost()           { return inner.cost() + 3; }
    public String description() { return inner.description() + " + кориця"; }
}

// СКЛАДАННЯ — обгортки нанизуються в рантаймі, як конструктор
Beverage order = new Cinnamon(new Milk(new Coffee()));
order.description();  // "кава + молоко + кориця"
order.cost();         // 28
