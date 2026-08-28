// Один Product на всю систему — приречений мішок суперечностей
class Product {
  // поля каталогу
  title: string;
  description: string | null;   // складу й доставці — null
  photos: string[];             // складу й доставці — порожньо
  reviews: Review[];            // тут узагалі чуже

  // поля складу
  weightKg: number | null;      // каталогу — null, поки склад не зважив
  shelf: string | null;
  stock: number | null;

  // поля доставки
  fragile: boolean | null;
  canLayFlat: boolean | null;

  // ...і так до сімдесяти полів, половина вічно порожня

  canPublish(): boolean {
    // правило каталогу
    return this.description !== null && this.photos.length > 0;
  }
  canStore(): boolean {
    // правило складу — і воно нічого не знає про правило каталогу
    return this.weightKg !== null;
  }
  // щойно створений товар: canPublish() = false, canStore() = false.
  // Він валідний чи ні? Клас не знає — бо намагається служити всім.
}
