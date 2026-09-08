/**
 * cli.ts — Головна точка входу консольної утиліти: завантаження декларативних правил,
 * координація конвеєра приймального шлюзу та повернення коду завершення для CI/CD.
 */

import * as fs from 'node:fs';
import * as http from 'node:http';
import * as path from 'node:path';
import { AlienationCertifier } from './alienation-certifier.ts';
import { BootstrapMonitor } from './bootstrap-monitor.ts';
import { LockfileValidator } from './lockfile-validator.ts';
import { SmokeRunner } from './smoke-runner.ts';
import type {
  AcceptancePolicy,
  AlienationCertificate,
  GateResults,
} from './types.ts';

export class AcceptanceGate {
  private lockValidator = new LockfileValidator();
  private bootstrapMonitor = new BootstrapMonitor();
  private smokeRunner = new SmokeRunner();
  private certifier = new AlienationCertifier();

  /**
   * Запускає повний цикл приймального аудиту системи згідно з політикою.
   */
  public async evaluate(
    policy: AcceptancePolicy,
    projectDir: string,
    baseUrl?: string,
    readinessCheck?: () => Promise<boolean>
  ): Promise<AlienationCertificate> {
    console.log(`\n======================================================`);
    console.log(`  ПРИЙМАЛЬНИЙ ШЛЮЗ АУДИТУ: ${policy.projectName}   `);
    console.log(`======================================================\n`);

    // ФАЗА 1: Перевірка lockfile та детермінованості версій
    console.log(`[1/3] Аудит цілісності lockfile та герметичності залежностей...`);
    const pkgPath = path.join(projectDir, 'package.json');
    const lockPath = path.join(projectDir, 'package-lock.json');

    const pkgRaw = fs.existsSync(pkgPath) ? fs.readFileSync(pkgPath, 'utf-8') : '{}';
    const lockRaw = fs.existsSync(lockPath) ? fs.readFileSync(lockPath, 'utf-8') : '{}';

    const lockResult = this.lockValidator.validate(pkgRaw, lockRaw, policy);
    console.log(
      `  -> Результат: ${lockResult.passed ? 'УСПІХ' : 'ЗБІЙ'} (${lockResult.totalDependencies} залежностей)`
    );

    // ФАЗА 2: Моніторинг бюджету часу холодного старту (Cold-Start SLA)
    console.log(`[2/3] Верифікація бюджету часу холодного старту (SLA)...`);
    const checkFn = readinessCheck ?? (async () => true);
    const bootstrapResult = await this.bootstrapMonitor.measureColdStart(
      checkFn,
      policy.maxBootstrapTimeMs
    );
    console.log(
      `  -> Результат: ${bootstrapResult.passed ? 'УСПІХ' : 'ЗБІЙ'} (${bootstrapResult.coldStartTimeMs}мс / бюджет ${policy.maxBootstrapTimeMs}мс)`
    );

    // ФАЗА 3: Виконання наскрізних димових HTTP-сценаріїв
    console.log(`[3/3] Виконання наскрізних димових HTTP-сценаріїв...`);
    let smokeResult;
    if (baseUrl && policy.smokeEndpoints.length > 0) {
      smokeResult = await this.smokeRunner.run(baseUrl, policy.smokeEndpoints);
      console.log(
        `  -> Результат: ${smokeResult.passed ? 'УСПІХ' : 'ЗБІЙ'} (${smokeResult.passedProbes}/${smokeResult.totalProbes} перевірок)`
      );
    } else {
      console.log(`  -> Димові тести пропущено (baseUrl не задано)`);
      smokeResult = {
        passed: true,
        totalProbes: 0,
        passedProbes: 0,
        failedProbes: 0,
        results: [],
      };
    }

    const gateResults: GateResults = {
      lockfile: lockResult,
      bootstrap: bootstrapResult,
      smoke: smokeResult,
    };

    const checksum = this.certifier.computeRepositoryChecksum(projectDir);
    const cert = this.certifier.generateCertificate(
      policy.projectName,
      checksum,
      gateResults
    );

    return cert;
  }
}

/**
 * Автономний демонстраційний запуск приймального аудиту.
 */
async function runDemo(): Promise<number> {
  const tmpDir = path.join(process.cwd(), '.demo_tmp_contractor_audit');
  fs.mkdirSync(tmpDir, { recursive: true });

  // Створюємо демонстраційний package.json
  fs.writeFileSync(
    path.join(tmpDir, 'package.json'),
    JSON.stringify(
      {
        name: 'contractor-service',
        version: '1.0.0',
        dependencies: {
          express: '4.19.2', // Строга фіксація без ^ чи ~
        },
      },
      null,
      2
    )
  );

  // Створюємо демонстраційний package-lock.json
  fs.writeFileSync(
    path.join(tmpDir, 'package-lock.json'),
    JSON.stringify(
      {
        name: 'contractor-service',
        lockfileVersion: 3,
        packages: {
          '': { name: 'contractor-service', version: '1.0.0' },
          'node_modules/express': {
            version: '4.19.2',
            resolved: 'https://registry.npmjs.org/express/-/express-4.19.2.tgz',
            integrity: 'sha512-5gbiCrS50Pvp2gKy0zU1...',
          },
        },
      },
      null,
      2
    )
  );

  // Запуск локального тестового HTTP-сервера для димових перевірок
  const server = http.createServer((req, res) => {
    if (req.url === '/healthz') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok', uptime: 1.2 }));
    } else if (req.url === '/api/v1/orders' && req.method === 'POST') {
      res.writeHead(201, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ orderId: 'ord_9901', status: 'created' }));
    } else {
      res.writeHead(404);
      res.end();
    }
  });

  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', () => resolve()));
  const address = server.address() as { port: number };
  const baseUrl = `http://127.0.0.1:${address.port}`;

  const policy: AcceptancePolicy = {
    projectName: 'CorePaymentGateway',
    maxBootstrapTimeMs: 1500,
    strictVersionPinning: true,
    disallowedPackageRegistries: ['http://'],
    smokeEndpoints: [
      {
        name: 'Readiness Probe',
        path: '/healthz',
        method: 'GET',
        expectedStatus: 200,
        maxLatencyMs: 300,
      },
      {
        name: 'Create Order Transaction',
        path: '/api/v1/orders',
        method: 'POST',
        expectedStatus: 201,
        maxLatencyMs: 500,
        payload: { amount: 150, currency: 'UAH' },
      },
    ],
  };

  const gate = new AcceptanceGate();
  const certifier = new AlienationCertifier();

  const cert = await gate.evaluate(
    policy,
    tmpDir,
    baseUrl,
    async () => {
      // Симуляція перевірки готовності сокета
      return true;
    }
  );

  const reportMd = certifier.formatReportMarkdown(cert);
  console.log('\n' + reportMd + '\n');

  // Збереження сертифіката
  const certPath = path.join(tmpDir, 'alienation_certificate.json');
  const reportPath = path.join(tmpDir, 'alienation_report.md');
  fs.writeFileSync(certPath, JSON.stringify(cert, null, 2), 'utf-8');
  fs.writeFileSync(reportPath, reportMd, 'utf-8');
  console.log(`Сертифікат відчужуваності збережено у: ${certPath}`);

  // Коректне закриття сервера з очікуванням колбека
  await new Promise<void>((resolve) => server.close(() => resolve()));

  // Прибирання тимчасової теки
  fs.rmSync(tmpDir, { recursive: true, force: true });

  return cert.acceptanceVerdict === 'ACCEPTED' ? 0 : 1;
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const isDemo = args.includes('--demo') || args.length === 0;

  let code = 0;
  if (isDemo) {
    code = await runDemo();
  } else {
    // Запуск на конкретній директорії користувача
    const dirIndex = args.indexOf('--dir');
    const projectDir = dirIndex !== -1 && args[dirIndex + 1] ? args[dirIndex + 1] : process.cwd();

    const urlIndex = args.indexOf('--url');
    const baseUrl = urlIndex !== -1 ? args[urlIndex + 1] : undefined;

    const defaultPolicy: AcceptancePolicy = {
      projectName: path.basename(path.resolve(projectDir)),
      maxBootstrapTimeMs: 3000,
      strictVersionPinning: true,
      smokeEndpoints: [
        {
          name: 'Default Health Check',
          path: '/healthz',
          method: 'GET',
          expectedStatus: 200,
          maxLatencyMs: 500,
        },
      ],
    };

    const gate = new AcceptanceGate();
    const cert = await gate.evaluate(defaultPolicy, projectDir, baseUrl);
    const certifier = new AlienationCertifier();
    console.log(certifier.formatReportMarkdown(cert));
    code = cert.acceptanceVerdict === 'ACCEPTED' ? 0 : 1;
  }

  process.exitCode = code;
}

main().catch((err) => {
  console.error('Критична помилка виконання приймального шлюзу:', err);
  process.exitCode = 1;
});
