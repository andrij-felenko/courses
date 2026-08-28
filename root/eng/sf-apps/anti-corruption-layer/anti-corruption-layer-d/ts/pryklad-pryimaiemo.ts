// БЕЗ шару: чужий формат розповзається по доменному коду
class OrderService {
  place(dto: CrmOrderDto): void {
    const parts = dto.sku.split("/");       // знання про їхній формат — тут
    const article = parts[0];
    const color = parts[1];                  // а завтра формат зміниться…
    if (dto.qty < 0) { /* якось окремо на повернення */ }
    if (dto.status_code === 7) {             // магічне число в домені
      // тягнемо чуже поняття "зарезервовано деінде" у свою модель
    }
    const clientId = dto.client_ref.slice(3); // зрізаємо "CL:"
    // …і так у кожному місці, що торкається замовлення
  }
}
