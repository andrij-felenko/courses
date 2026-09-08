package com.company.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

class DomainArchitectureTest {

    private static JavaClasses productionClasses;

    @BeforeAll
    static void loadBytecode() {
        // Одноразовий імпорт байткоду для прискорення виконання всіх тестів класу
        productionClasses = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                .importPackages("com.company.order..");
    }

    @Test
    @DisplayName("Доменне ядро не повинно залежати від інфраструктури чи сторонніх драйверів")
    void domainLayerMustRemainPure() {
        // Формулювання правила за допомогою текучого інтерфейсу
        ArchRule domainIsolationRule = noClasses()
                .that().resideInAPackage("..domain..")
                .should().dependOnClassesThat().resideInAnyPackage(
                        "..infrastructure..",
                        "..presentation..",
                        "org.postgresql..",
                        "org.springframework.web.."
                )
                .as("Ізоляція чистого доменного ядра від зовнішніх адаптерів")
                .because("бізнес-логіка повинна залежати лише від внутрішніх абстракцій і залишатися незалежною від деталей зберігання та транспорту");

        // Виконання перевірки графу класів
        domainIsolationRule.check(productionClasses);
    }
}
