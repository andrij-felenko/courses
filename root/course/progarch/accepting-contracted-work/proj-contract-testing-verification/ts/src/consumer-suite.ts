import { ContractorClient, DeliverableNotFoundError } from "./client.ts";
import type { Interaction } from "./contract.ts";
import { ConsumerMockServer } from "./mock-server.ts";

/**
 * Набір споживчих тестів (Consumer Tests).
 * Реєструє очікування споживача, перевіряє поведінку клієнтського коду
 * та вивантажує узгоджений JSON-контракт.
 */
export async function runConsumerSuite(contractOutputPath: string): Promise<void> {
  const mockServer = new ConsumerMockServer();
  await mockServer.start();
  const baseUrl = mockServer.getBaseUrl();
  const client = new ContractorClient(baseUrl);

  console.log(`[Споживчі тести] Мок-сервер запущено на ${baseUrl}`);

  try {
    // -------------------------------------------------------------
    // Сценарій 1: Успішне отримання переданого акта робіт (ID: 101)
    // -------------------------------------------------------------
    const getDeliverableInteraction: Interaction = {
      description: "Отримання даних акта робіт для перевірки статусу",
      providerState: "акт робіт 101 передано підрядником на рецензування",
      request: {
        method: "GET",
        path: "/deliverables/101",
        headers: { Accept: "application/json" },
      },
      response: {
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: {
          id: "101",
          title: "Модуль криптографічної автентифікації",
          contractor: "ПП Безпека-Систем",
          status: "SUBMITTED",
          artifactsCount: 5,
        },
      },
    };

    mockServer.addInteraction(getDeliverableInteraction);

    const deliverable = await client.getDeliverable("101");
    if (deliverable.id !== "101" || deliverable.status !== "SUBMITTED") {
      throw new Error(`[Тест 1 провалено]: неочікувані дані акта: ${JSON.stringify(deliverable)}`);
    }
    console.log("  ✓ Сценарій 1: Успішне читання зданого акта робіт пройдено");

    // -------------------------------------------------------------
    // Сценарій 2: Обробка ситуації відсутності акта (HTTP 404)
    // -------------------------------------------------------------
    const notFoundInteraction: Interaction = {
      description: "Запит неіснуючого акта робіт повертає 404",
      providerState: "акт робіт 999 відсутній у реєстрі",
      request: {
        method: "GET",
        path: "/deliverables/999",
        headers: { Accept: "application/json" },
      },
      response: {
        status: 404,
        headers: { "Content-Type": "application/json" },
        body: {
          error: "Акт робіт з номером 999 не знайдено",
        },
      },
    };

    mockServer.addInteraction(notFoundInteraction);

    let caught404 = false;
    try {
      await client.getDeliverable("999");
    } catch (err) {
      if (err instanceof DeliverableNotFoundError && err.id === "999") {
        caught404 = true;
      } else {
        throw err;
      }
    }

    if (!caught404) {
      throw new Error("[Тест 2 провалено]: клієнт не викинув DeliverableNotFoundError для 404");
    }
    console.log("  ✓ Сценарій 2: Обробка помилки 404 (відсутній акт) пройдена");

    // -------------------------------------------------------------
    // Сценарій 3: Затвердження акта робіт підрядника (POST)
    // -------------------------------------------------------------
    const acceptInteraction: Interaction = {
      description: "Підписання акта приймання робіт замовником",
      providerState: "акт робіт 101 очікує на підписання",
      request: {
        method: "POST",
        path: "/deliverables/101/accept",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: {
          acceptedBy: "Головний архітектор замовника",
          comment: "Код аудійовано, навантажувальні тести успішні",
        },
      },
      response: {
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: {
          id: "101",
          status: "ACCEPTED",
          acceptedAt: "2026-09-09T00:00:00.000Z",
        },
      },
    };

    mockServer.addInteraction(acceptInteraction);

    const acceptResult = await client.acceptDeliverable("101", {
      acceptedBy: "Головний архітектор замовника",
      comment: "Код аудійовано, навантажувальні тести успішні",
    });

    if (acceptResult.id !== "101" || acceptResult.status !== "ACCEPTED") {
      throw new Error(`[Тест 3 провалено]: некоректний результат приймання: ${JSON.stringify(acceptResult)}`);
    }
    console.log("  ✓ Сценарій 3: Успішне приймання робіт через POST пройдено");

    // -------------------------------------------------------------
    // Верифікація виконання всіх очікувань та генерація контракту
    // -------------------------------------------------------------
    const contract = mockServer.verifyAndEmitContract(
      "CustomerPortal",
      "ContractorVendorService",
      contractOutputPath
    );

    console.log(`[Споживчі тести] Контракт успішно записано до ${contractOutputPath}`);
    console.log(`  Всього взаємодій у контракті: ${contract.interactions.length}`);
  } finally {
    await mockServer.stop();
  }
}
