package com.company.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

class ComponentIsolationArchitectureTest {

    private static JavaClasses projectClasses;

    @BeforeAll
    static void initClasspath() {
        // Імпорт виробничого байткоду з виключенням тестів
        projectClasses = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                .importPackages("com.company.order..");
    }

    @Test
    @DisplayName("Класи внутрішньої реалізації сервісів не повинні бути публічними")
    void internalServicesShouldBePackagePrivate() {
        // Захист інкапсуляції: класи з підпакету internal не мають бути доступні ззовні
        ArchRule encapsulationRule = classes()
                .that().resideInAPackage("..service.internal..")
                .should().notBePublic()
                .as("Інкапсуляція внутрішніх сервісних компонентів")
                .because("деталі реалізації повинні бути сховані на рівні пакету й не розширювати публічний інтерфейс");

        encapsulationRule.check(projectClasses);
    }

    @Test
    @DisplayName("Сутності домену не повинні використовувати анотації персистентності JPA або серіалізації Jackson")
    void domainEntitiesMustBePureFromFrameworkAnnotations() {
        // Заборона інфраструктурних анотацій у бізнес-моделях
        ArchRule pureDomainEntitiesRule = noClasses()
                .that().resideInAPackage("..domain.model..")
                .should().beAnnotatedWith("javax.persistence.Entity")
                .orShould().beAnnotatedWith("jakarta.persistence.Entity")
                .orShould().beAnnotatedWith("com.fasterxml.jackson.annotation.JsonProperty")
                .as("Чистота доменних сутностей від інфраструктурних анотацій")
                .because("доменне ядро не повинно залежати від бібліотек серіалізації або ORM-фреймворків");

        pureDomainEntitiesRule.check(projectClasses);
    }

    @Test
    @DisplayName("Інфраструктурні репозиторії повинні обов'язково реалізовувати інтерфейси доменних портів")
    void infrastructureRepositoriesMustImplementDomainPorts() {
        // Контроль інверсії залежностей: кожен адаптер бази даних має реалізовувати контракт домену
        ArchRule repositoryImplementationRule = classes()
                .that().resideInAPackage("..infrastructure.persistence..")
                .and().haveSimpleNameEndingWith("RepositoryImpl")
                .should().implement(com.company.order.domain.port.OrderRepository.class)
                .as("Реалізація доменних портів інфраструктурними адаптерами")
                .because("інфраструктура зобов'язана виконувати контракти, визначені предметною областю");

        repositoryImplementationRule.check(projectClasses);
    }
}
