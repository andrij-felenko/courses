// Сутність бази даних із лінивою асоціацією
@Entity
@Table(name = "orders")
public class OrderEntity {
    @Id
    private UUID id;
    private BigDecimal totalAmount;

    // Ліниве завантаження за замовчуванням
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    private CustomerEntity customer;

    public UUID getId() { return id; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public CustomerEntity getCustomer() { return customer; }
}

public class OrderDto {
    private UUID id;
    private BigDecimal totalAmount;
    // ModelMapper намагається викликати order.getCustomer().getName()
    private String customerName;

    public void setId(UUID id) { this.id = id; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    public void setCustomerName(String customerName) { this.customerName = customerName; }
}

@Service
public class OrderQueryService {
    @Autowired private OrderRepository orderRepository;
    @Autowired private ModelMapper modelMapper;

    @Transactional(readOnly = true)
    public List<OrderDto> getRecentOrders(int limit) {
        // 1. Виконується 1 SQL-запит: отримання списку із 100 замовлень
        List<OrderEntity> orders = orderRepository.findRecent(PageRequest.of(0, limit));

        // 2. Під час копіювання ModelMapper смикає геттер getCustomer()
        // Проксі Hibernate перехоплює виклик і надсилає 100 окремих запитів до бази:
        // SELECT * FROM customers WHERE id = ?
        return orders.stream()
            .map(order -> modelMapper.map(order, OrderDto.class))
            .toList();
    }
}
