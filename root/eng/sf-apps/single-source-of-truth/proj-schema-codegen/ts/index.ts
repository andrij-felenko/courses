// Згенеровано автоматично з user_profile.proto — НЕ РЕДАГУВАТИ ВРУЧНУ

export enum SubscriptionTier {
  TIER_UNSPECIFIED = 0,
  TIER_FREE = 1,
  TIER_STANDARD = 2,
  TIER_PREMIUM = 3,
}

export interface UserProfileDTO {
  accountId: string;      // 64-бітні числа транслюються в рядок для точності в JS
  email: string;
  balanceCents: number;
  tier: SubscriptionTier;
  isSuspended: boolean;
  updatedAtMs: number;
}

export interface UpdateEmailRequestDTO {
  accountId: string;
  newEmail: string;
}

// Клієнтський клас для безпечної взаємодії з бекендом
export class BillingClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  // Отримання канонічного профілю з сервера
  async fetchProfile(accountId: string): Promise<UserProfileDTO> {
    const response = await fetch(`${this.baseUrl}/v1/accounts/${accountId}`);
    if (!response.ok) {
      throw new Error(`Помилка отримання профілю: статус ${response.status}`);
    }
    const data: UserProfileDTO = await response.json();
    return data;
  }

  // Обчислення форматованого балансу в гривнях (похідне подання для UI)
  formatBalanceUah(profile: UserProfileDTO): string {
    const uah = profile.balanceCents / 100;
    return new Intl.NumberFormat('uk-UA', {
      style: 'currency',
      currency: 'UAH',
    }).format(uah);
  }
}
