// TypeScript / Node.js еквівалент промислового конвеєра

export enum Currency {
    UAH = "UAH",
    USD = "USD",
    EUR = "EUR",
    UNKNOWN = "UNKNOWN"
}

export enum CanonicalOrderStatus {
    Created = "CREATED",
    Paid = "PAID",
    Shipped = "SHIPPED",
    Cancelled = "CANCELLED"
}

export interface CanonicalLineItem {
    sku: string;
    quantity: number;
    unitPriceCents: bigint;
}

export interface CanonicalMessageHeader {
    messageId: string;
    correlationId: string;
    schemaVersion: string;
    timestampUtcMs: number;
    originSystem: string;
}

export interface CanonicalOrderPayload {
    orderId: string;
    customerId: string;
    totalAmountCents: bigint;
    currency: Currency;
    status: CanonicalOrderStatus;
    items: CanonicalLineItem[];
}

export interface CanonicalOrderMessage {
    header: CanonicalMessageHeader;
    payload: CanonicalOrderPayload;
}

export class InboundTranslator {
    static parseCurrency(code: string): Currency {
        switch (code.toUpperCase()) {
            case "UAH": return Currency.UAH;
            case "USD": return Currency.USD;
            case "EUR": return Currency.EUR;
            default: return Currency.UNKNOWN;
        }
    }

    static fromPartnerWebhook(raw: any, correlationId: string): CanonicalOrderMessage {
        const orderTotal = Number(raw.order_total || 0);
        if (orderTotal < 0) {
            throw new Error("Partner Webhook Error: від'ємна сума замовлення");
        }
        const cents = BigInt(Math.round(orderTotal * 100));

        let status = CanonicalOrderStatus.Cancelled;
        if (raw.state_str === "SUCCESS" || raw.state_str === "COMPLETED") {
            status = CanonicalOrderStatus.Paid;
        } else if (raw.state_str === "NEW") {
            status = CanonicalOrderStatus.Created;
        }

        const qty = Number(raw.item_count) || 1;

        return {
            header: {
                messageId: `msg-ext-${raw.ext_order_ref}`,
                correlationId,
                schemaVersion: "2.0.0",
                timestampUtcMs: Date.now(),
                originSystem: `PARTNER_${raw.partner_id}`
            },
            payload: {
                orderId: `PARTNER-${raw.ext_order_ref}`,
                customerId: `USER-${raw.user_email}`,
                totalAmountCents: cents,
                currency: this.parseCurrency(String(raw.curr || "")),
                status,
                items: [{
                    sku: String(raw.item_sku || ""),
                    quantity: qty,
                    unitPriceCents: cents / BigInt(qty)
                }]
            }
        };
    }
}

export class CanonicalSchemaValidator {
    static validate(msg: CanonicalOrderMessage): void {
        if (!msg.header.correlationId) throw new Error("Validation Error: відсутній correlationId");
        if (!msg.header.messageId) throw new Error("Validation Error: відсутній messageId");
        if (!msg.payload.orderId) throw new Error("Validation Error: порожній orderId");
        if (msg.payload.currency === Currency.UNKNOWN) throw new Error("Validation Error: невідома валюта");
        if (msg.payload.totalAmountCents <= 0n) throw new Error("Validation Error: сума повинна бути більшою за 0");
        if (msg.payload.items.length === 0) throw new Error("Validation Error: список товарів порожній");
    }
}
