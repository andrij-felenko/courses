package com.company.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.library.Architectures;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.library.Architectures.layeredArchitecture;
import static com.tngtech.archunit.library.Architectures.onionArchitecture;

class SystemLayersArchitectureTest {

    private static JavaClasses systemClasses;

    @BeforeAll
    static void loadBytecode() {
        systemClasses = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                .importPackages("com.company.order..");
    }

    @Test
    @DisplayName("Багатошарова архітектура сервісу повинна суворо дотримуватися допустимих векторів доступу")
    void verifyLayeredArchitecture() {
        ArchRule layersRule = layeredArchitecture()
                .consideringAllDependencies()
                // 1. Оголошення логічних шарів системи
                .layer("Presentation").definedBy("..order.presentation..", "..order.controller..")
                .layer("Application").definedBy("..order.application..")
                .layer("Domain").definedBy("..order.domain..")
                .layer("Infrastructure").definedBy("..order.infrastructure..")

                // 2. Встановлення обмежень на доступ до шарів
                .whereLayer("Presentation").mayNotBeAccessedByAnyLayer()
                .whereLayer("Application").mayOnlyBeAccessedByLayers("Presentation", "Infrastructure")
                .whereLayer("Domain").mayOnlyBeAccessedByLayers("Application", "Infrastructure")
                .whereLayer("Infrastructure").mayNotBeAccessedByAnyLayer()

                .as("Контроль чистої багатошарової архітектури сервісу замовлень")
                .because("порушення напрямків викликів між шарами руйнує модульність та унеможливлює підтримку коду");

        layersRule.check(systemClasses);
    }

    @Test
    @DisplayName("Верифікація центрострімких залежностей через спеціалізований DSL Onion Architecture")
    void verifyOnionArchitecture() {
        ArchRule onionRule = onionArchitecture()
                .domainModels("..order.domain.model..")
                .domainServices("..order.domain.service..")
                .applicationServices("..order.application..")
                .adapter("persistence", "..order.infrastructure.persistence..")
                .adapter("messaging", "..order.infrastructure.messaging..")
                .adapter("web", "..order.infrastructure.web..")
                .as("Захист центрострімких зв'язків цибулевої архітектури")
                .because("зовнішні адаптери не повинні протікати в серцевину бізнес-моделі");

        onionRule.check(systemClasses);
    }
}
