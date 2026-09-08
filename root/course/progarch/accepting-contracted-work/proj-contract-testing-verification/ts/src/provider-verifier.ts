import type { Contract, Interaction } from "./contract.ts";
import { loadContract, matchPayload } from "./contract.ts";
import { ProviderService } from "./provider-service.ts";

/** Результат верифікації окремої контрактної взаємодії */
export interface InteractionVerificationResult {
  interactionDescription: string;
  providerState: string;
  success: boolean;
  errors: string[];
}

/** Загальний звіт верифікації контракту */
export interface VerificationReport {
  contractFile: string;
  totalInteractions: number;
  passedCount: number;
  failedCount: number;
  results: InteractionVerificationResult[];
}

/**
 * Верифікатор провайдера (Provider Verifier).
 * Завантажує JSON-контракт від споживача, ініціалізує необхідний стан
 * на стороні реального провайдера та відтворює контрактні HTTP-запити.
 */
export class ProviderVerifier {
  private readonly providerBaseUrl: string;

  constructor(providerBaseUrl: string) {
    this.providerBaseUrl = providerBaseUrl;
  }

  /**
   * Виконати повну перевірку контракту проти запущеного провайдера.
   */
  public async verifyContract(contractFilePath: string): Promise<VerificationReport> {
    const contract: Contract = loadContract(contractFilePath);
    const results: InteractionVerificationResult[] = [];

    console.log(`[Верифікатор провайдера] Перевірка контракту для споживача "${contract.consumer.name}"`);
    console.log(`  Провайдер: ${contract.provider.name}`);
    console.log(`  Кількість взаємодій: ${contract.interactions.length}`);

    for (let i = 0; i < contract.interactions.length; i++) {
      const interaction = contract.interactions[i];
      console.log(`\n  Взаємодія #${i + 1}: ${interaction.description}`);
      console.log(`    Стан: "${interaction.providerState}"`);

      const errors: string[] = [];

      try {
        // 1. Налаштовуємо стан провайдера
        await this.setProviderState(interaction.providerState);

        // 2. Відтворюємо запит
        const targetUrl = `${this.providerBaseUrl}${interaction.request.path}`;
        const fetchOptions: RequestInit = {
          method: interaction.request.method,
          headers: interaction.request.headers || {},
        };

        if (interaction.request.body !== undefined) {
          fetchOptions.body = JSON.stringify(interaction.request.body);
        }

        const res = await fetch(targetUrl, fetchOptions);

        // 3. Звіряємо статус-код
        if (res.status !== interaction.response.status) {
          errors.push(
            `Невідповідність HTTP-статусу: очікувався ${interaction.response.status}, фактично ${res.status}`
          );
        }

        // 4. Звіряємо корисне навантаження
        if (interaction.response.body !== undefined) {
          const actualBody = await res.json();
          const matchResult = matchPayload(interaction.response.body, actualBody);
          if (!matchResult.matches) {
            errors.push(...matchResult.differences);
          }
        }

        if (errors.length === 0) {
          console.log("    ✓ Взаємодія успішно підтверджена");
        } else {
          console.error("    ✗ Помилки під час верифікації:");
          for (const err of errors) {
            console.error(`      - ${err}`);
          }
        }
      } catch (err) {
        errors.push(`Виняток під час запиту до провайдера: ${String(err)}`);
        console.error(`    ✗ Помилка мережі або виконання: ${String(err)}`);
      }

      results.push({
        interactionDescription: interaction.description,
        providerState: interaction.providerState,
        success: errors.length === 0,
        errors,
      });
    }

    const passedCount = results.filter((r) => r.success).length;
    const failedCount = results.length - passedCount;

    return {
      contractFile: contractFilePath,
      totalInteractions: results.length,
      passedCount,
      failedCount,
      results,
    };
  }

  private async setProviderState(state: string): Promise<void> {
    const stateUrl = `${this.providerBaseUrl}/_provider_state`;
    const res = await fetch(stateUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state }),
    });

    if (!res.ok) {
      throw new Error(`Не вдалося налаштувати стан провайдера "${state}": HTTP ${res.status}`);
    }
  }
}

/**
 * Автономний запуск повної верифікації провайдера з підняттям тестового екземпляра сервера.
 */
export async function runProviderVerification(contractFilePath: string): Promise<boolean> {
  const providerService = new ProviderService();
  await providerService.start();
  const providerUrl = providerService.getBaseUrl();

  try {
    const verifier = new ProviderVerifier(providerUrl);
    const report = await verifier.verifyContract(contractFilePath);

    console.log("\n=======================================================");
    console.log("[Підсумок верифікації контракту провайдером]");
    console.log(`  Всього взаємодій : ${report.totalInteractions}`);
    console.log(`  Успішно          : ${report.passedCount}`);
    console.log(`  Провалено        : ${report.failedCount}`);
    console.log("=======================================================\n");

    return report.failedCount === 0;
  } finally {
    await providerService.stop();
  }
}
