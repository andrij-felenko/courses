import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.factory.Mappers;

// 1. Декларативний контракт перетворення
@Mapper
public interface OrderMapper {
    OrderMapper INSTANCE = Mappers.getMapper(OrderMapper.class);

    @Mapping(source = "customer.name", target = "customerName")
    OrderDto entityToDto(OrderEntity order);
}

// 2. Код, який MapStruct генерує у каталозі збірки (target/generated-sources):
public class OrderMapperImpl implements OrderMapper {
    @Override
    public OrderDto entityToDto(OrderEntity order) {
        if (order == null) {
            return null;
        }

        OrderDto orderDto = new OrderDto();
        orderDto.setId(order.getId());
        orderDto.setTotalAmount(order.getTotalAmount());

        // Пряме звернення без рефлексії:
        if (order.getCustomer() != null) {
            orderDto.setCustomerName(order.getCustomer().getName());
        }

        return orderDto;
    }
}
