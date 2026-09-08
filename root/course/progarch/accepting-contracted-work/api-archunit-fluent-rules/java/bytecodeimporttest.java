package com.company.architecture;

import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;

class BytecodeImportTest {

    @Test
    @DisplayName("Імпорт байткоду виробничих класів сервісу замовлень без тестового оточення")
    void shouldImportProductionClassesSuccessfully() {
        // Створення імпортера з виключенням тестового коду та сторонніх архівів
        ClassFileImporter importer = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_JARS)
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_ARCHIVES);

        // Рекурсивне зчитування байткоду пакетів сервісу замовлень
        JavaClasses importedClasses = importer.importPackages("com.company.order..");

        // Перевірка коректності завантаження моделі в пам'ять
        assertNotNull(importedClasses, "Об'єктний граф JavaClasses має бути успішно створений");
        assertFalse(importedClasses.isEmpty(), "Імпортер повинен знайти щонайменше один виробничий клас");

        // Пошук конкретної бізнес-сутності в об'єктній моделі
        JavaClass orderEntity = importedClasses.get(com.company.order.domain.Order.class);
        assertNotNull(orderEntity, "Клас Order повинен бути присутній у завантаженому графі");

        // Інспекція кількості прямих вихідних залежностей сутності
        int outgoingDependenciesCount = orderEntity.getDirectDependenciesFromSelf().size();
        System.out.println("Клас Order має прямих залежностей: " + outgoingDependenciesCount);
    }
}
