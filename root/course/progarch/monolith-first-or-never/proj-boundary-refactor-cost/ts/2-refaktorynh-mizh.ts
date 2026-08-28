// TypeScript — Мережева взаємодія та обробка відмов між мікросервісами
export enum NetworkErrorCode {
    Timeout = "TIMEOUT",
    ServiceUnavailable = "SERVICE_UNAVAILABLE"
}

export interface DiscountResponse {
    discountAmount: number;
    appliedRule: string;
}

export class PricingServiceClient {
    public async fetchRemoteDiscount(customerId: string, subtotal: number, promo?: string): Promise<DiscountResponse> {
        // Симуляція асинхронної мережевої затримки (5 мс)
        await new Promise(resolve => setTimeout(resolve, 5));

        let discountRate = 0;
        if (subtotal >= 200.0) {
            discountRate += 0.15;
        } else if (subtotal >= 100.0) {
            discountRate += 0.10;
        }

        if (promo === "VIP_SUMMER") {
            discountRate += 0.05;
        }

        return {
            discountAmount: subtotal * discountRate,
            appliedRule: "REMOTE_PRICING_V1"
        };
    }
}

export class DistributedOrderService {
    private pricingClient = new PricingServiceClient();

    public async processOrderCheckout(customerId: string, subtotal: number, promo?: string): Promise<number> {
        let discount = 0;

        try {
            // Асинхронний мережевий виклик крізь сокети ядра Linux
            const response = await this.pricingClient.fetchRemoteDiscount(customerId, subtotal, promo);
            discount = response.discountAmount;
        } catch (error) {
            // Обробка часткової відмови мережевої ланки
            console.warn("PricingService timeout, fallback to zero discount");
            discount = 0;
        }

        return subtotal - discount;
    }
}

// Демонстрація виконання
(async () => {
    const service = new DistributedOrderService();
    const startTime = performance.now();
    const total = await service.processOrderCheckout("CUST-1092", 210.0, "VIP_SUMMER");
    const endTime = performance.now();

    console.log("=== МІКРОСЕРВІСНА АРХІТЕКТУРА (TypeScript) ===");
    console.log(`Підсумкова вартість: $${total}`);
    console.log(`Час виконання: ${(endTime - startTime).toFixed(2)} мс`);
})();
