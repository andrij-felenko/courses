import type {
  AcceptDeliverableRequest,
  AcceptDeliverableResponse,
  Deliverable,
} from "./contract.ts";

/** Помилка відсутності запитуваного артефакту робіт */
export class DeliverableNotFoundError extends Error {
  public readonly id: string;

  constructor(id: string) {
    super(`Акт робіт підрядника з ідентифікатором ${id} не знайдено`);
    this.name = "DeliverableNotFoundError";
    this.id = id;
  }
}

/** Загальна помилка виклику API підрядника */
export class ContractorApiError extends Error {
  public readonly statusCode: number;
  public readonly responseBody?: unknown;

  constructor(
    message: string,
    statusCode: number,
    responseBody?: unknown
  ) {
    super(message);
    this.name = "ContractorApiError";
    this.statusCode = statusCode;
    this.responseBody = responseBody;
  }
}

/**
 * Клієнтський HTTP-адаптер замовника для взаємодії з API підрядника.
 * Виконує строго типізовані виклики та транслює HTTP-відповіді в доменні структури.
 */
export class ContractorClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Отримати поточний стан акта робіт підрядника за його ID.
   */
  public async getDeliverable(id: string): Promise<Deliverable> {
    const url = `${this.baseUrl}/deliverables/${encodeURIComponent(id)}`;
    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    if (response.status === 404) {
      throw new DeliverableNotFoundError(id);
    }

    if (!response.ok) {
      const errText = await response.text();
      throw new ContractorApiError(
        `Помилка отримання акта робіт: HTTP ${response.status}`,
        response.status,
        errText
      );
    }

    return (await response.json()) as Deliverable;
  }

  /**
   * Виконати формальне приймання та затвердження виконаної роботи.
   */
  public async acceptDeliverable(
    id: string,
    payload: AcceptDeliverableRequest
  ): Promise<AcceptDeliverableResponse> {
    const url = `${this.baseUrl}/deliverables/${encodeURIComponent(id)}/accept`;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.status === 404) {
      throw new DeliverableNotFoundError(id);
    }

    if (!response.ok) {
      const errText = await response.text();
      throw new ContractorApiError(
        `Помилка затвердження робіт підрядника: HTTP ${response.status}`,
        response.status,
        errText
      );
    }

    return (await response.json()) as AcceptDeliverableResponse;
  }
}
