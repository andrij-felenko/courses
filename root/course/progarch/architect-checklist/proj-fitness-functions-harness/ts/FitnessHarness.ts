// FitnessHarness.ts — Архітектурний контролер для TypeScript / Node.js / Microservices
import { readFileSync } from 'fs';

export interface ServiceSpec {
  name: string;
  layer: 'Domain' | 'Application' | 'Infrastructure';
  dependencies: string[];
  circuitBreakerEnabled: boolean;
  networkTimeoutMs: number;
  w3cTracingEnabled: boolean;
}

export interface RuleViolation {
  ruleId: string;
  message: string;
  isBlocker: boolean;
}

export class ArchitectureFitnessChecker {
  constructor(private readonly services: ServiceSpec[]) {}

  public validateArchitecture(): { passed: boolean; violations: RuleViolation[] } {
    const violations: RuleViolation[] = [];

    for (const service of this.services) {
      // 1. Clean Architecture boundary enforcement
      if (service.layer === 'Domain') {
        const forbiddenDep = service.dependencies.find(
          (dep) => dep.includes('Infrastructure') || dep.includes('HttpAdapter')
        );
        if (forbiddenDep) {
          violations.push({
            ruleId: 'RULE-01-DOMAIN-ISOLATION',
            message: `Доменний сервіс ${service.name} прямо залежить від ${forbiddenDep}`,
            isBlocker: true,
          });
        }
      }

      // 2. Resilience and Timeout budget
      if (service.dependencies.length > 0) {
        if (service.networkTimeoutMs > 1000 || service.networkTimeoutMs <= 0) {
          violations.push({
            ruleId: 'RULE-02-TIMEOUT-BUDGET',
            message: `Сервіс ${service.name} перевищує ліміт затримки: ${service.networkTimeoutMs}мс`,
            isBlocker: true,
          });
        }
        if (!service.circuitBreakerEnabled) {
          violations.push({
            ruleId: 'RULE-03-CIRCUIT-BREAKER',
            message: `Сервіс ${service.name} не має Circuit Breaker для зовнішніх викликів`,
            isBlocker: true,
          });
        }
      }

      // 3. Observability tracing context
      if (!service.w3cTracingEnabled) {
        violations.push({
          ruleId: 'RULE-04-TRACING-CONTEXT',
          message: `Втрачено W3C Trace Context у сервісі ${service.name}`,
          isBlocker: false,
        });
      }
    }

    const hasBlockers = violations.some((v) => v.isBlocker);
    return { passed: !hasBlockers, violations };
  }
}
