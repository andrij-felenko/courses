export interface ServiceDependency {
  sourceService: string;
  targetService: string;
  isSynchronousHttp: boolean;
  sharesDatabaseSchema: boolean;
}

export class ArchitectureFitnessChecker {
  public static verifyNoDistributedMonolith(dependencies: ServiceDependency[]): void {
    const violations: string[] = [];

    for (const dep of dependencies) {
      if (dep.sharesDatabaseSchema) {
        violations.push(
          `ПОШКОДЖЕННЯ МЕЖІ: Сервіс [${dep.sourceService}] має прямий доступ до СУБД сервісу [${dep.targetService}]. Спільні схеми заборонені!`
        );
      }
    }

    if (violations.length > 0) {
      console.error('\n❌ ФІТНЕС-ФУНКЦІЯ ЗАВАЛИЛА ЗБІРКУ CI/CD:');
      violations.forEach((v) => console.error(`  - ${v}`));
      throw new Error('Архітектурний регрес: Спроба побудови Розподіленого Моноліта!');
    }

    console.log('✅ ФІТНЕС-ФУНКЦІЯ ПРОЙДЕНА: Архітектурні межі суворі. Зчеплення за даними відсутнє.');
  }
}
