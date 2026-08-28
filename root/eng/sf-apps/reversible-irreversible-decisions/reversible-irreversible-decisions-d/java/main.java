// Java, ArchUnit: правило архітектури як звичайний тест — падає на білді
@AnalyzeClasses(packages = "com.shop")
class SeamGuardTest {
    @ArchTest
    static final ArchRule db_driver_stays_behind_the_adapter =
        noClasses()
            .that().resideOutsideOfPackage("..persistence.adapter..")
            .should().dependOnClassesThat().resideInAPackage("org.postgresql..");
    // будь-який імпорт драйвера повз адаптер = червоний білд
}
