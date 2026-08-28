// platform-client.ts — Робочий TypeScript SDK платформи для Stream-команд
import { v4 as uuidv4 } from 'uuid';

export interface DatabaseProvisionSpec {
  serviceName: string;
  teamId: string;
  dbName: string;
  allocatedStorageGb: number;
  enableHa?: boolean;
  backupRetentionDays?: number;
}

export interface ResourceResult {
  resourceId: string;
  connectionSecretRef: string;
  status: 'READY' | 'FAILED';
  allocatedEndpoints: string[];
}

export class DHPlatformException extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DHPlatformException';
  }
}

export class DigitalHomesPlatformClient {
  private readonly endpoint: string;
  private readonly apiToken: string;

  constructor(endpoint: string, apiToken: string) {
    this.endpoint = endpoint.replace(/\/+$/, '');
    this.apiToken = apiToken;
  }

  async provisionPostgresDatabase(
    spec: DatabaseProvisionSpec,
    idempotencyKey?: string
  ): Promise<ResourceResult> {
    const key = idempotencyKey || uuidv4();
    const url = `${this.endpoint}/v1/resources/postgresql`;

    console.log(`[PlatformClient] Запит БД '${spec.dbName}' для команди '${spec.teamId}'...`);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiToken}`,
        'Content-Type': 'application/json',
        'X-Idempotency-Key': key,
        'X-DH-Client-Version': '2.4.0-ts',
      },
      body: JSON.stringify({
        serviceName: spec.serviceName,
        teamId: spec.teamId,
        dbName: spec.dbName,
        allocatedStorageGb: spec.allocatedStorageGb,
        enableHa: spec.enableHa ?? true,
        backupRetentionDays: spec.backupRetentionDays ?? 30,
      }),
    });

    if (response.status !== 202) {
      const errText = await response.text();
      throw new DHPlatformException(`Платформа відхилила запит (${response.status}): ${errText}`);
    }

    const { jobId } = await response.json() as { jobId: string };
    console.log(`[PlatformClient] Запит прийнято. JobID: ${jobId}. Опитування стану...`);

    return this.pollJobCompletion(jobId);
  }

  private async pollJobCompletion(jobId: string, maxWaitMs: number = 180000): Promise<ResourceResult> {
    const startTime = Date.now();
    const pollUrl = `${this.endpoint}/v1/jobs/${jobId}`;

    while (Date.now() - startTime < maxWaitMs) {
      try {
        const res = await fetch(pollUrl, {
          headers: { 'Authorization': `Bearer ${this.apiToken}` },
        });

        if (res.ok) {
          const data = await res.json() as { status: string; resultResource?: ResourceResult; error?: string };
          if (data.status === 'COMPLETED' && data.resultResource) {
            console.log(`[PlatformClient] Ресурс готовий за ${(Date.now() - startTime) / 1000}s!`);
            return data.resultResource;
          }
          if (data.status === 'FAILED') {
            throw new DHPlatformException(`Створення ресурсу завершилося помилкою: ${data.error}`);
          }
        }
      } catch (err) {
        if (err instanceof DHPlatformException) throw err;
        console.warn(`[PlatformClient] Тимчасовий збій мережі під час опитування: ${err}`);
      }

      await new Promise((r) => setTimeout(r, 4000));
    }

    throw new DHPlatformException(`Перевищено час очікування платформи (${maxWaitMs / 1000}s)`);
  }
}
