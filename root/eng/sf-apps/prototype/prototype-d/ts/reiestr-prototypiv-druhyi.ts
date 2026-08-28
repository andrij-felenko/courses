class ShapeRegistry {
  private prototypes = new Map<string, Shape>();

  register(key: string, proto: Shape) {   // покласти зразок під ключем
    this.prototypes.set(key, proto);
  }
  create(key: string): Shape {
    const proto = this.prototypes.get(key);
    if (!proto) throw new Error(`немає прототипу: ${key}`);
    return proto.clone();                  // новий об'єкт — копія зразка
  }
}

const registry = new ShapeRegistry();
registry.register("коло", new Circle(0, 0, 10));   // зразок налаштовано раз
const c = registry.create("коло");                 // далі — лише копії
