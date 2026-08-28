// Полів у класі немає — вони приїдуть зі схеми. Але компілятору про них треба сказати окремо.
interface Order {
  id: number | null;
  customer_id: string;
  total: number;
  status: string;
  lock_version: number;
}
class Order extends Model {
  static table = "orders";
  static version = "lock_version";
  static db = db;

  canCancel(): boolean {
    return this.status === "new" || this.status === "paid";
  }
}
