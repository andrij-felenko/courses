// Семантичні категорії доменних помилок ядра
export type DomainErrorKind = 'NotFound' | 'RuleViolation' | 'Conflict' | 'AccessDenied';

export interface DomainError {
  readonly kind: DomainErrorKind;
  readonly message: string;
  readonly invalidParams?: Record<string, string>;
}

// Типізований результат виконання сценарію (патерн Result)
export type Result<T> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: DomainError };

// Протокольна відповідь HTTP-адаптера
export interface HttpResponse {
  readonly status: number;
  readonly headers: Record<string, string>;
  readonly body: string;
}

// Структура документа помилки за стандартом RFC 7807 (Problem Details)
export interface ProblemDetails {
  readonly type: string;
  readonly title: string;
  readonly status: number;
  readonly detail: string;
  readonly invalidParams?: Record<string, string>;
}

// Обробник результату (Result Mapper): трансляція доменного результату в HTTP
export class HttpResultMapper {
  static toResponse<T>(result: Result<T>, successStatus = 200): HttpResponse {
    if (result.ok) {
      return {
        status: successStatus,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result.value),
      };
    }

    const { status, title } = this.mapStatus(result.error.kind);
    const problem: ProblemDetails = {
      type: `https://api.digitalhomes.io/errors/${result.error.kind.toLowerCase()}`,
      title,
      status,
      detail: result.error.message,
      ...(result.error.invalidParams ? { invalidParams: result.error.invalidParams } : {}),
    };

    return {
      status,
      headers: { 'Content-Type': 'application/problem+json' },
      body: JSON.stringify(problem),
    };
  }

  private static mapStatus(kind: DomainErrorKind): { status: number; title: string } {
    switch (kind) {
      case 'NotFound':
        return { status: 404, title: 'Ресурс не знайдено' };
      case 'RuleViolation':
        return { status: 422, title: 'Порушення бізнес-правила' };
      case 'Conflict':
        return { status: 409, title: 'Конфлікт стану ресурсу' };
      case 'AccessDenied':
        return { status: 403, title: 'Доступ заборонено' };
    }
  }
}
