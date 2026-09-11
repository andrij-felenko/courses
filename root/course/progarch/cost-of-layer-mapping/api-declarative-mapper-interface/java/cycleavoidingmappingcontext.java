package com.digitalhomes.order.adapter.mapping;

import org.mapstruct.*;
import java.util.*;

// Контекст для збереження ідентичності об'єктів і зупинки циклічної рекурсії
public class CycleAvoidingMappingContext {
    private final Map<Object, Object> knownInstances = new IdentityHashMap<>();

    @BeforeMapping
    public <T> T getMappedInstance(Object source, @TargetType Class<T> targetType) {
        // Якщо екземпляр уже трансформувався, повертаємо його з карти
        return targetType.cast(knownInstances.get(source));
    }

    @BeforeMapping
    public void storeMappedInstance(Object source, @MappingTarget Object target) {
        // Реєструємо цільовий об'єкт до обходу його дочірніх зв'язків
        knownInstances.put(source, target);
    }
}

// Декларативний мапер з політиками оновлення та обробки null
@Mapper(
    componentModel = MappingConstants.ComponentModel.SPRING,
    nullValueMappingStrategy = NullValueMappingStrategy.RETURN_DEFAULT,
    nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE
)
public interface OrderMapper {

    // Автоматичний мапінг колекції: компілятор згенерує цикл на базі toItemDto
    List<OrderItemDto> toItemDtoList(List<OrderItem> items, @Context CycleAvoidingMappingContext context);

    // Мапінг графа з передачею контексту для розриву взаємних посилань
    @Mapping(target = "items", source = "items")
    OrderDto toDto(Order order, @Context CycleAvoidingMappingContext context);

    @Mapping(target = "order", source = "order")
    OrderItemDto toItemDto(OrderItem item, @Context CycleAvoidingMappingContext context);

    // Оновлення наявного екземпляра без нових алокацій у купі (heap)
    // Поля зі значенням null у запиті ігноруються й не затирають стан сутності
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "items", ignore = true)
    void updateEntityFromPatch(OrderPatchRequest request, @MappingTarget Order target);
}
