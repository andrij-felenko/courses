import * as fs from 'fs';
import * as path from 'path';
import * as ts from 'typescript';
import { AstAnalyzer } from './ast-analyzer';
import { CallGraphBuilder } from './call-graph-builder';
import { createSampleProjectProgram } from './fixtures/sample-project';
import { ReportGenerator } from './report-generator';
import { AuditReport, CliOptions } from './types';
import { UtilityCategorizer } from './utility-categorizer';

/**
 * Консольний додаток аудиту звалища утиліт.
 * Керує життєвим циклом CLI, парсить прапорці командного рядка,
 * координує конвеєр компілятора TypeScript, відображає результати
 * та генерує системний exit code для CI/CD.
 */
export class CliApplication {
  private readonly reportGenerator = new ReportGenerator();
  private readonly categorizer = new UtilityCategorizer(2);

  /**
   * Головний метод виконання утиліти.
   */
  public async run(argv: string[]): Promise<number> {
    const options = this.parseArguments(argv);

    if (options.showHelp) {
      this.printHelp();
      return 0;
    }

    try {
      let program: ts.Program;
      let targetUtilsFiles: string[];
      let projectRoot: string;

      if (options.demoMode || !options.projectPath) {
        // Режим автономного стенду: створюємо віртуальну програму на базі фікстури
        const demoSetup = createSampleProjectProgram();
        program = demoSetup.program;
        targetUtilsFiles = demoSetup.utilsFiles;
        projectRoot = '/virtual-sample-project';
      } else {
        // Режим реального проєкту: парсимо tsconfig.json або файлову структуру
        const projectSetup = this.createRealProjectProgram(
          options.projectPath,
          options.utilsPath
        );
        program = projectSetup.program;
        targetUtilsFiles = projectSetup.utilsFiles;
        projectRoot = path.resolve(options.projectPath);
      }

      // ЕТАП 1: Обхід AST через TypeScript Compiler API та пошук витоків типів
      const analyzer = new AstAnalyzer(program);
      const exportedFunctions = analyzer.analyzeFiles(targetUtilsFiles);

      // ЕТАП 2: Трасування викликів та побудова графа міжмодульних залежностей
      const graphBuilder = new CallGraphBuilder(program, exportedFunctions);
      const callGraph = graphBuilder.build();

      // ЕТАП 3: Категоризація функцій за принципами CRP та REP
      const categorized = this.categorizer.categorize(
        exportedFunctions,
        callGraph
      );
      const summary = this.categorizer.summarize(categorized);

      // Формування фінального звіту
      const exitCode = summary.hasViolations ? 1 : 0;
      const report: AuditReport = {
        timestamp: new Date().toISOString(),
        projectRoot,
        summary,
        utilities: categorized,
        exitCode,
      };

      // ЕТАП 4: Вивід результатів
      if (options.jsonOutput) {
        console.log(this.reportGenerator.generateJson(report));
      } else {
        console.log(this.reportGenerator.generateConsoleReport(report));
      }

      // Збереження JSON-файла за потреби
      if (options.outputFilePath) {
        const outPath = path.resolve(options.outputFilePath);
        fs.writeFileSync(
          outPath,
          this.reportGenerator.generateJson(report),
          'utf-8'
        );
        console.log(`[ІНФО] Машинозчитуваний JSON-звіт збережено у: ${outPath}`);
      }

      return exitCode;
    } catch (error) {
      console.error('[КРИТИЧНА ПОМИЛКА АУДИТУ]:', error);
      return 2;
    }
  }

  /**
   * Парсить аргументи командного рядка.
   */
  private parseArguments(argv: string[]): CliOptions {
    const options: CliOptions = {
      demoMode: false,
      jsonOutput: false,
      showHelp: false,
    };

    for (let i = 0; i < argv.length; i++) {
      const arg = argv[i];
      if (arg === '--demo' || arg === '-d') {
        options.demoMode = true;
      } else if (arg === '--json') {
        options.jsonOutput = true;
      } else if (arg === '--help' || arg === '-h') {
        options.showHelp = true;
      } else if (arg === '--project' || arg === '-p') {
        options.projectPath = argv[++i];
      } else if (arg === '--utils' || arg === '-u') {
        options.utilsPath = argv[++i];
      } else if (arg === '--output' || arg === '-o') {
        options.outputFilePath = argv[++i];
      }
    }

    return options;
  }

  /**
   * Створює ts.Program для реального каталогу на диску.
   */
  private createRealProjectProgram(
    projectPath: string,
    customUtilsPath?: string
  ): { program: ts.Program; utilsFiles: string[] } {
    const absoluteRoot = path.resolve(projectPath);
    let configPath = ts.findConfigFile(
      absoluteRoot,
      ts.sys.fileExists,
      'tsconfig.json'
    );

    let rootNames: string[] = [];
    let options: ts.CompilerOptions = {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
    };

    if (configPath) {
      const configFile = ts.readConfigFile(configPath, ts.sys.readFile);
      const parsed = ts.parseJsonConfigFileContent(
        configFile.config,
        ts.sys,
        path.dirname(configPath)
      );
      rootNames = parsed.fileNames;
      options = parsed.options;
    } else {
      // Якщо tsconfig немає, скануємо директорію вручну
      const files: string[] = [];
      const scanDir = (dir: string): void => {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
          const full = path.join(dir, entry.name);
          if (entry.isDirectory() && entry.name !== 'node_modules') {
            scanDir(full);
          } else if (entry.isFile() && full.endsWith('.ts')) {
            files.push(full);
          }
        }
      };
      scanDir(absoluteRoot);
      rootNames = files;
    }

    const program = ts.createProgram(rootNames, options);

    // Визначаємо цільові файли утиліт
    const utilsFilter = customUtilsPath
      ? path.resolve(customUtilsPath).replace(/\\/g, '/')
      : '/utils/';

    const utilsFiles = rootNames.filter((f) =>
      f.replace(/\\/g, '/').includes(utilsFilter)
    );

    return { program, utilsFiles };
  }

  /**
   * Виводить довідку по командах.
   */
  private printHelp(): void {
    console.log(`
ВИКОРИСТАННЯ:
  npx ts-node src/cli.ts [ОПЦІЇ]

ОПЦІЇ:
  --demo, -d          Запустити аналіз автономного демонстраційного стенду (за замовчуванням)
  --project, -p <шлях> Шлях до кореня проєкту або файлу tsconfig.json
  --utils, -u <шлях>   Шлях або патерн каталогу утиліт для аудиту (за замовчуванням: **/utils/**)
  --json              Вивести структурований JSON-звіт у стандартний вивід
  --output, -o <файл> Зберегти JSON-звіт у вказаний файл для CI/CD
  --help, -h          Показати цю довідку

КОДИ ЗАВЕРШЕННЯ (EXIT CODES):
  0 - Успіх: порушень не виявлено (усі утиліти відповідають CRP/REP)
  1 - Помилка архітектури: виявлено мертвий код, одноразові хелпери або витік домену
  2 - Системна помилка запуску
`);
  }
}

// Точка безпосереднього запуску з термінала
if (require.main === module) {
  const cli = new CliApplication();
  cli.run(process.argv.slice(2)).then((code) => {
    process.exit(code);
  });
}
