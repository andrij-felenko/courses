// notification-renderer.ts
// Мультиканальний рушій рендерингу та локалізації сповіщень

export type Channel = 'email' | 'push' | 'sms' | 'in_app';

export interface RecipientContext {
  userId: string;
  locale: string;       // BCP 47: 'uk-UA', 'en-US'
  timezone: string;     // IANA: 'Europe/Kyiv'
  channels: Channel[];
}

export interface EventPayload {
  orderId: string;
  customerName: string;
  amountCents: number;
  currency: string;
  itemsCount: number;
  createdAtUtc: string; // ISO 8601 UTC
}

// Типи вузлів синтаксичного дерева AST
export type ASTNode =
  | { type: 'literal'; value: string }
  | { type: 'variable'; key: string }
  | { type: 'currency'; key: string; currencyKey: string }
  | { type: 'datetime'; key: string; dateStyle: 'short' | 'medium' | 'long' }
  | { 
      type: 'plural'; 
      key: string; 
      variants: Record<string, ASTNode[]> 
    };

export interface ChannelTemplates {
  emailSubject: ASTNode[];
  emailHtmlBody: ASTNode[];
  pushTitle: ASTNode[];
  pushBody: ASTNode[];
  smsBody: ASTNode[];
}

export interface RenderedArtifacts {
  email?: {
    subject: string;
    html: string;
    text: string;
  };
  push?: {
    title: string;
    body: string;
    payloadJson: string;
  };
  sms?: {
    text: string;
    encoding: 'GSM-7' | 'UCS-2';
    characterCount: number;
    segmentCount: number;
  };
}

// 1. Безпечне екранування за контекстом (XSS / Injection Protection)
export class ContextEscaper {
  static escapeHtml(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  static stripHtmlToPlaintext(html: string): string {
    return html
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '$2 ($1)')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/p>/gi, '\n\n')
      .replace(/<[^>]+>/g, '')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#039;/g, "'")
      .trim();
  }
}

// 2. Аналізатор кодування та сегментації SMS (GSM 03.38 vs UCS-2)
export class SmsBudgetMeter {
  // Набір базових 7-бітних символів GSM-7
  private static readonly GSM7_BASIC = new Set(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?" +
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`abcdefghijklmnopqrstuvwxyzäöñüà"
  );

  static analyze(text: string): { encoding: 'GSM-7' | 'UCS-2'; count: number; segments: number } {
    let isGsm7 = true;
    for (const char of text) {
      if (!this.GSM7_BASIC.has(char)) {
        isGsm7 = false;
        break;
      }
    }

    const count = Array.from(text).length; // Враховуємо сурогатні пари Unicode

    if (isGsm7) {
      // 160 символів на 1 сегмент, або 153 символи при розбитті на кілька (UDH заголовок)
      const segments = count <= 160 ? 1 : Math.ceil(count / 153);
      return { encoding: 'GSM-7', count, segments };
    } else {
      // UCS-2: 70 символів на 1 сегмент, або 67 символів при розбитті на кілька
      const segments = count <= 70 ? 1 : Math.ceil(count / 67);
      return { encoding: 'UCS-2', count, segments };
    }
  }
}

// 3. Компілятор та обчислювач AST-дерева в ізольованій пісочниці
export class NotificationRenderer {
  // Кеш форматувальників для уникнення повторного створення важких екземплярів Intl
  private pluralRulesCache = new Map<string, Intl.PluralRules>();
  private numberFormatCache = new Map<string, Intl.NumberFormat>();
  private dateTimeFormatCache = new Map<string, Intl.DateTimeFormat>();

  private getPluralCategory(count: number, locale: string): string {
    let rule = this.pluralRulesCache.get(locale);
    if (!rule) {
      rule = new Intl.PluralRules(locale);
      this.pluralRulesCache.set(locale, rule);
    }
    return rule.select(count);
  }

  private formatCurrency(amountCents: number, currency: string, locale: string): string {
    const key = `${locale}_${currency}`;
    let fmt = this.numberFormatCache.get(key);
    if (!fmt) {
      fmt = new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency,
        currencyDisplay: 'narrowSymbol'
      });
      this.numberFormatCache.set(key, fmt);
    }
    return fmt.format(amountCents / 100);
  }

  private formatDateTime(isoString: string, timezone: string, locale: string): string {
    const key = `${locale}_${timezone}`;
    let fmt = this.dateTimeFormatCache.get(key);
    if (!fmt) {
      fmt = new Intl.DateTimeFormat(locale, {
        timeZone: timezone,
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      this.dateTimeFormatCache.set(key, fmt);
    }
    return fmt.format(new Date(isoString));
  }

  // Обчислення списку вузлів AST для заданого контексту
  public evaluateAst(
    nodes: ASTNode[], 
    payload: Record<string, any>, 
    recipient: RecipientContext,
    isHtmlContext: boolean
  ): string {
    let result = '';

    for (const node of nodes) {
      switch (node.type) {
        case 'literal':
          result += node.value;
          break;

        case 'variable': {
          const rawVal = payload[node.key] !== undefined ? String(payload[node.key]) : '';
          result += isHtmlContext ? ContextEscaper.escapeHtml(rawVal) : rawVal;
          break;
        }

        case 'currency': {
          const cents = Number(payload[node.key]) || 0;
          const curr = String(payload[node.currencyKey] || 'USD');
          const formatted = this.formatCurrency(cents, curr, recipient.locale);
          result += isHtmlContext ? ContextEscaper.escapeHtml(formatted) : formatted;
          break;
        }

        case 'datetime': {
          const iso = String(payload[node.key] || new Date().toISOString());
          const formatted = this.formatDateTime(iso, recipient.timezone, recipient.locale);
          result += isHtmlContext ? ContextEscaper.escapeHtml(formatted) : formatted;
          break;
        }

        case 'plural': {
          const count = Number(payload[node.key]) || 0;
          const category = this.getPluralCategory(count, recipient.locale);
          
          // Вибір гілки: точний збіг категорії CLDR або fallback на 'other'
          const branch = node.variants[category] || node.variants['other'] || [];
          
          // Підставляємо значення лічильника в контекст вкладеної гілки
          const subPayload = { ...payload, '#': count };
          result += this.evaluateAst(branch, subPayload, recipient, isHtmlContext);
          break;
        }
      }
    }

    return result;
  }

  // Головний конвеєр рендерингу для всіх підтримуваних каналів
  public renderNotification(
    templates: ChannelTemplates,
    payload: EventPayload,
    recipient: RecipientContext
  ): RenderedArtifacts {
    const artifacts: RenderedArtifacts = {};
    const rawPayload = payload as unknown as Record<string, any>;

    // 1. Канал Email
    if (recipient.channels.includes('email')) {
      const subject = this.evaluateAst(templates.emailSubject, rawPayload, recipient, false);
      const innerHtml = this.evaluateAst(templates.emailHtmlBody, rawPayload, recipient, true);
      
      // Вбудовування у глобальний Responsive Email Layout з інлайновими стилями
      const fullHtml = `<!DOCTYPE html>
<html lang="${recipient.locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${ContextEscaper.escapeHtml(subject)}</title>
</head>
<body style="margin:0;padding:24px;background-color:#f4f6f8;font-family:'Segoe UI',sans-serif;color:#1a1a1a;">
  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center">
        <table role="presentation" width="600" border="0" cellspacing="0" cellpadding="0" style="background-color:#ffffff;border-radius:8px;padding:32px;border:1px solid #e2e8f0;">
          <tr>
            <td>
              ${innerHtml}
            </td>
          </tr>
          <tr>
            <td style="padding-top:24px;border-top:1px solid #e2e8f0;font-size:12px;color:#64748b;text-align:center;">
              Ви отримали цей лист, оскільки зареєстровані на сервісі.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

      const textFallback = ContextEscaper.stripHtmlToPlaintext(fullHtml);
      artifacts.email = { subject, html: fullHtml, text: textFallback };
    }

    // 2. Канал Push (APNs / FCM)
    if (recipient.channels.includes('push')) {
      const title = this.evaluateAst(templates.pushTitle, rawPayload, recipient, false);
      const body = this.evaluateAst(templates.pushBody, rawPayload, recipient, false);
      
      // Формування службового JSON з контролем ліміту 4096 байтів
      const pushObj = {
        aps: {
          alert: { title, body },
          sound: 'default',
          badge: 1
        },
        data: {
          orderId: payload.orderId,
          clickAction: `/orders/${payload.orderId}`
        }
      };
      
      let pushJson = JSON.stringify(pushObj);
      const byteLength = Buffer.byteLength(pushJson, 'utf8');
      
      if (byteLength > 4096) {
        // Якщо перевищено ліміт APNs — акуратно скорочуємо поле body
        const truncatedBody = body.slice(0, 100) + '...';
        pushObj.aps.alert.body = truncatedBody;
        pushJson = JSON.stringify(pushObj);
      }

      artifacts.push = { title, body, payloadJson: pushJson };
    }

    // 3. Канал SMS
    if (recipient.channels.includes('sms')) {
      const text = this.evaluateAst(templates.smsBody, rawPayload, recipient, false);
      const budget = SmsBudgetMeter.analyze(text);
      
      artifacts.sms = {
        text,
        encoding: budget.encoding,
        characterCount: budget.count,
        segmentCount: budget.segments
      };
    }

    return artifacts;
  }
}
