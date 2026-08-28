type OrderRow = {
  id: string;
  customer_id: string;
  total: number;
  status: string;
  created_at: string;   // ISO-8601 у UTC — як у колонці timestamptz
};

// той самий мапер, яким користується SqlOrderRepository
const toRow = (o: Order): OrderRow => ({
  id: o.id,
  customer_id: o.customerId,
  total: o.total,
  status: o.status,
  created_at: o.createdAt.toISOString(),
});

const toDomain = (r: OrderRow): Order =>
  new Order(r.id, r.customer_id, r.total, new Date(r.created_at), r.status as OrderStatus);
