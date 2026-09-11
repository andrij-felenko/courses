package com.digitalhomes.order.adapter.mapping;

import org.mapstruct.*;

// Доменна сутність з інкапсульованим станом та валідацією інваріантів
public class Apartment {
    private final String number;
    private final double totalArea;
    private final double livingArea;

    // Конструктор гарантує, що об'єкт неможливо створити в невалідному стані
    public Apartment(String number, double totalArea, double livingArea) {
        this.number = number;
        this.totalArea = totalArea;
        this.livingArea = livingArea;
        validateInvariants();
    }

    public void validateInvariants() {
        if (totalArea <= 0) {
            throw new IllegalArgumentException("Загальна площа повинна бути додатною");
        }
        if (livingArea > totalArea) {
            throw new IllegalStateException("Житлова площа не може перевищувати загальну");
        }
    }

    public String getNumber() { return number; }
    public double getTotalArea() { return totalArea; }
    public double getLivingArea() { return livingArea; }
}

// Мапер, що викликає конструктор та хуки валідації
@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public abstract class ApartmentDomainMapper {

    // Хук перевірки попередніх умов перед початком мапінгу
    @BeforeMapping
    protected void sanitizeRequest(ApartmentCreateRequest request) {
        if (request.number() == null || request.number().isBlank()) {
            throw new IllegalArgumentException("Номер квартири є обов'язковим");
        }
    }

    // Компілятор зіставить поля DTO з аргументами конструктора Apartment
    public abstract Apartment toDomain(ApartmentCreateRequest request);

    // Хук фінальної перевірки після створення об'єкта
    @AfterMapping
    protected void verifyState(@MappingTarget Apartment apartment) {
        apartment.validateInvariants();
    }
}
