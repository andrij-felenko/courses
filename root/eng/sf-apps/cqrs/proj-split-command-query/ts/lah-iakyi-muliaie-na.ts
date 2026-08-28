// РОУТИНГ читання за свіжістю: свій щойно змінений — з боку запису, решта — зі знімка
class OrderViewRouter {
  constructor(private write: OrderRepository,
              private read: OrderReadStore) {}

  forScreen(id: string, opts: { justChangedByUser: boolean }): OrderView {
    if (opts.justChangedByUser) {
      const o = this.write.byId(id);        // свіжо, повільно — read-your-writes
      return { id: o.id, customerName: o.customerName(), total: o.total(), status: o.status };
    }
    const snap = this.read.byId(id);        // швидко, може відставати
    return { id: snap!.id, customerName: snap!.customerName,
             total: snap!.total, status: snap!.status };
  }
}
