// Контекст КАТАЛОГУ: товар — це те, що показують і продають
namespace Catalog {
  class Product {
    constructor(
      private title: string,
      private description: string,   // не nullable: без опису товару каталогу не існує
      private photos: string[],
    ) {
      if (photos.length === 0) throw new Error("товар каталогу без фото не буває");
    }
    // тут немає ваги й полиці — вони цьому світу не потрібні
  }
}

// Контекст СКЛАДУ: товар — це фізична одиниця зберігання
namespace Warehouse {
  class Product {
    constructor(
      private sku: string,
      private weightKg: number,      // не nullable: без ваги на склад не приймають
      private shelf: string,
    ) {}
    // тут немає опису й відгуків — складу байдуже
  }
}
