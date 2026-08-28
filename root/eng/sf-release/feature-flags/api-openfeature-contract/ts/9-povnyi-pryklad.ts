import { OpenFeature, Hook, HookContext, EvaluationDetails } from "@openfeature/server-sdk";
import { MyInMemoryProvider } from "./my-in-memory-provider";

// 1. Створюємо хук для логування A/B-експозицій
class ExposureLoggingHook implements Hook {
  after(hookContext: HookContext, details: EvaluationDetails<any>) {
    if (details.reason === "SPLIT") {
      console.log(`[Telemetry] User "${hookContext.context.targetingKey}" assigned to variant "${details.variant}" for flag "${details.flagKey}"`);
    }
  }
}

// 2. Реєструємо глобального провайдера та хуки на рівні платформи
await OpenFeature.setProviderAndWait(new MyInMemoryProvider());
OpenFeature.addHooks(new ExposureLoggingHook());

// 3. Отримуємо типізованого клієнта для платіжного сервісу
const client = OpenFeature.getClient("billing-service");

// 4. Обчислюємо прапорець під час обробки транзакції
async function processCheckout(userId: string, country: string, amount: number) {
  const context = {
    targetingKey: userId,
    country: country,
    cartAmount: amount
  };

  // Виклик ніколи не кидає винятків: при збої повертається false
  const useStripeV2 = await client.getBooleanValue("payment-gateway-v2", false, context);

  if (useStripeV2) {
    return executeStripeV2Checkout(amount);
  } else {
    return executeLegacyCheckout(amount);
  }
}
