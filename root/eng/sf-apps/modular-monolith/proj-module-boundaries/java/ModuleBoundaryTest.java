// architecture/ModuleBoundaryTest.java — запускається як звичайний тест у CI
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

class ModuleBoundaryTest {

    // сканується один раз: усі класи застосунку
    private final JavaClasses app =
        new ClassFileImporter().importPackages("shop..");

    // ПРАВИЛО 1: нутрощі warehouse — приватні для всіх, крім самого warehouse
    @Test void warehouseInternalsAreHidden() {
        ArchRule rule = noClasses()
            .that().resideOutsideOfPackage("shop.warehouse..")
            .should().dependOnClassesThat().resideInAPackage("shop.warehouse.internal..")
            .because("ззовні дозволено лише фасад shop.warehouse.api");

        rule.check(app);   // ← кине AssertionError зі списком порушників
    }

    // ПРАВИЛО 2: напрям стрілки — orders може знати warehouse, але не навпаки
    @Test void warehouseDoesNotDependOnOrders() {
        ArchRule rule = noClasses()
            .that().resideInAPackage("shop.warehouse..")
            .should().dependOnClassesThat().resideInAPackage("shop.orders..")
            .because("склад нижче замовлень за потоком; зворотна стрілка = цикл");

        rule.check(app);
    }
}
