/**
 * types.ts — Оголошення інтерфейсів декларативної конфігурації шлюзу приймання,
 * правил SLA, результатів аудиту та структури сертифіката відчужуваності.
 */

export interface SmokeEndpointConfig {
  name: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT';
  expectedStatus: number;
  maxLatencyMs: number;
  payload?: Record<string, unknown>;
  headers?: Record<string, string>;
}

export interface AcceptancePolicy {
  projectName: string;
  maxBootstrapTimeMs: number;
  disallowedPackageRegistries?: string[];
  strictVersionPinning: boolean;
  smokeEndpoints: SmokeEndpointConfig[];
}

export interface DependencyViolation {
  name: string;
  version: string;
  reason: string;
}

export interface LockfileAuditResult {
  passed: boolean;
  totalDependencies: number;
  floatingVersions: DependencyViolation[];
  untrustedRegistries: { name: string; resolvedUrl: string }[];
  missingIntegrityHashes: string[];
}

export interface BootstrapAuditResult {
  passed: boolean;
  coldStartTimeMs: number;
  budgetMs: number;
  isWithinBudget: boolean;
  error?: string;
}

export interface ProbeResult {
  name: string;
  url: string;
  status: number;
  latencyMs: number;
  passed: boolean;
  error?: string;
}

export interface SmokeAuditResult {
  passed: boolean;
  totalProbes: number;
  passedProbes: number;
  failedProbes: number;
  results: ProbeResult[];
}

export interface GateResults {
  lockfile: LockfileAuditResult;
  bootstrap: BootstrapAuditResult;
  smoke: SmokeAuditResult;
}

export interface AlienationCertificate {
  version: string;
  issuedAt: string;
  project: string;
  repositoryChecksum: string;
  acceptanceVerdict: 'ACCEPTED' | 'REJECTED';
  gateResults: GateResults;
  summary: string;
}
