// ContextBoundaryTest.java — ArchUnit як звичайний JUnit-5-тест
@AnalyzeClasses(packages = "com.dh")
class ContextBoundaryTest {

  @ArchTest
  static final ArchRule billing_isolated_from_control =
      noClasses().that().resideInAPackage("..billing..")
          .should().dependOnClassesThat().resideInAPackage("..control..")
          .because("ADR-014: білінг — загальний контекст, ізольований від ядра керування");
}
