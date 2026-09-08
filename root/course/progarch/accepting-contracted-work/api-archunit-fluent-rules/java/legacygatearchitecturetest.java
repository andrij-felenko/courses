package com.company.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.freeze.FreezingArchRule.freeze;

class LegacyGateArchitectureTest {

    private static JavaClasses codebaseClasses;

    @BeforeAll
    static void loadClasses() {
        codebaseClasses = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                // Ігнорування синтетичних класів компілятора, які можуть давати хибні спрацьовування
                .withImportOption(location -> !location.contains("Lambda"))
                .importPackages("com.company.order..");
    }

    @Test
    @DisplayName("Заморожування наявних порушень: блокування лише нових нелегітимних імпортів у домені")
    void domainMustNotGainNewInfrastructureDependencies() {
        // Базове суворе правило ізоляції домену
        ArchRule strictDomainRule = noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAPackage("..infrastructure..")
                .as("Сувора ізоляція домену від інфраструктури")
                .because("нові компоненти підрядника не мають збільшувати технічний борг системи");

        // Обгортання правила у FreezingArchRule для захисту від нових дефектів
        ArchRule frozenRule = freeze(strictDomainRule);

        // Перевірка в CI: впаде лише у разі появи НОВИХ порушень
        frozenRule.check(codebaseClasses);
    }
}
