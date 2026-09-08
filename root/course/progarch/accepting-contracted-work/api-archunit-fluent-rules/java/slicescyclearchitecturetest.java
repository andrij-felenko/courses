package com.company.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices;

class SlicesCycleArchitectureTest {

    private static JavaClasses systemClasses;

    @BeforeAll
    static void loadBytecode() {
        systemClasses = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                .importPackages("com.company.order..");
    }

    @Test
    @DisplayName("Функціональні модулі системи повинні бути повністю вільними від взаємних циклів")
    void modulesMustBeFreeOfCycles() {
        // Виділення кожного підпакета всередині модуля як автономного зрізу
        ArchRule cycleFreeRule = slices()
                .matching("com.company.order.module.(*)..")
                .should().beFreeOfCycles()
                .as("Заборона циклічних залежностей між функціональними модулями")
                .because("модулі мають бути ациклічними для забезпечення незалежного тестування та подальшого масштабування");

        // Перевірка ациклічності графу зрізів
        cycleFreeRule.check(systemClasses);
    }
}
