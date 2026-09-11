package digitalhomes.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.Architectures.layeredArchitecture;

public class LayerIntegrityFitnessTest {

    private static JavaClasses codebaseClasses;

    @BeforeAll
    public static void scanCodebase() {
        // Завантаження метаданих скомпільованого байткоду всієї системи
        codebaseClasses = new ClassFileImporter().importPackages("digitalhomes");
    }

    @Test
    public void layeredArchitectureMustBeStrictlyRespected() {
        // Декларативний опис структури шарів і допустимих потоків керування
        ArchRule strictLayers = layeredArchitecture()
            .consideringAllDependencies()
            .layer("Presentation").definedBy("..presentation..")
            .layer("Application").definedBy("..application..")
            .layer("Domain").definedBy("..domain..")
            .layer("Infrastructure").definedBy("..infrastructure..")

            .whereLayer("Presentation").mayNotBeAccessedByAnyLayer()
            .whereLayer("Application").mayOnlyBeAccessedByLayers("Presentation", "Infrastructure")
            .whereLayer("Domain").mayOnlyBeAccessedByLayers("Application", "Infrastructure")
            .whereLayer("Infrastructure").mayOnlyBeAccessedByLayers("Application");

        strictLayers.check(codebaseClasses);
    }

    @Test
    public void domainLayerMustRemainPureWithoutInfrastructureImports() {
        // Заборона проникнення класів ORM, серіалізаторів та веб-фреймворків у домен
        ArchRule pureDomainRule = noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat()
            .resideInAnyPackage(
                "org.hibernate..",
                "jakarta.persistence..",
                "org.springframework.web..",
                "digitalhomes.infrastructure.."
            );

        pureDomainRule.check(codebaseClasses);
    }

    @Test
    public void controllersMustNotDirectlyAccessInfrastructureRepositories() {
        // Заборона прямого доступу з контролерів до інфраструктурних класів
        ArchRule noBypassRule = noClasses()
            .that().resideInAPackage("..presentation..")
            .should().dependOnClassesThat()
            .resideInAPackage("digitalhomes.infrastructure..");

        noBypassRule.check(codebaseClasses);
    }
}
