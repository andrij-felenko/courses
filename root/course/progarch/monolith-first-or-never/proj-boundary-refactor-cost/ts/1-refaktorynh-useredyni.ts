// TypeScript — Внутрішньопроцесорний рефакторинг у Модульному моноліті
export interface OrderItem {
    itemId: string;
    unitPrice: number;
    quantity: number;
}

export interface OrderContext {
    orderId: string;
    customerId: string;
    items: OrderItem[];
    promoCode?: string;
}

export class OrderModule {
    public calculateOrderTotal(ctx: OrderContext): number {
        // Step 1: Обчислення суми товарів у кошику
        const subtotal = ctx.items.reduce((acc, item) => acc + item.unitPrice * item.quantity, 0);

        // Step 2: Прямий виклик перенесеної логіки у тому самому об'єктному контексті
        const discount = this.calculateBulkDiscount(ctx.customerId, subtotal, ctx.promoCode);

        return subtotal - discount;
    }

    private calculateBulkDiscount(customerId: string, subtotal: number, promo?: string): number {
        let discountRate = 0;

        if (subtotal >= 200.0) {
            discountRate += 0.15;
        } else if (subtotal >= 100.0) {
            discountRate += 0.10;
        }

        if (promo === "VIP_SUMMER") {
            discountRate += 0.05;
        }

        return subtotal * discountRate;
    }
}

// Демонстрація виконання
const orderModule = new OrderModule();
const context: OrderContext = {
    orderId: "ORD-2026-8891",
    customerId: "CUST-1092",
    items: [
        { itemId: "LAPTOP-STAND", unitPrice: 45.0, quantity: 2 },
        { itemId: "MECHANICAL-KEYBOARD", unitPrice: 120.0, quantity: 1 }
    ],
    promoCode: "VIP_SUMMER"
};

const startTime = performance.now();
const total = orderModule.calculateOrderTotal(context);
const endTime = performance.now();

console.log("=== МОДУЛЬНИЙ МОНОЛІТ (TypeScript) ===");
console.log(`Підсумкова вартість: $${total}`);
console.log(`Час виконання: ${(endTime - startTime).toFixed(4)} мс`);
