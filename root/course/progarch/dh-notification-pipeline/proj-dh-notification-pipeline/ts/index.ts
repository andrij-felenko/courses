import { createHash } from "node:crypto";

export enum Severity {
  LOW = "LOW",
  DEFAULT = "DEFAULT",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum ChannelType {
  SILENT_PUSH = "SILENT_PUSH",
  CRITICAL_PUSH = "CRITICAL_PUSH",
  SMS_FALLBACK = "SMS_FALLBACK",
}

export interface HomeEvent {
  eventId: string;
  homeId: string;
  severity: Severity;
  eventType: string;
  title: string;
  body: string;
  timestamp: number;
  payload: Record<string, unknown>;
}

export interface UserPreference {
  userId: string;
  quietHoursStart: number; // Час початку тихих годин (наприклад, 23 для 23:00)
  quietHoursEnd: number;   // Час завершення тихих годин (наприклад, 7 для 07:00)
  isAwayMode: boolean;     // Режим "Відпустка / Немає вдома"
  optedOutTypes: Set<string>; // Категорії евентів, вимкнені користувачем
}

export interface UserDevice {
  deviceId: string;
  userId: string;
  pushToken: string;
  phoneNumber?: string;
  isIos: boolean;
}

export interface DeliveryTask {
  deliveryId: string;
  eventId: string;
  userId: string;
  deviceId: string;
  channel: ChannelType;
  title: string;
  body: string;
  tokenOrNumber: string;
  attempts: number;
}

/**
 * 1. PolicyEngine — перевірка відповідності події преференсіям мешканця
 */
export class PolicyEngine {
  shouldDeliver(
    event: HomeEvent,
    pref: UserPreference,
    currentHour: number
  ): { deliver: boolean; forceDigest: boolean } {
    // Інваріант 1: Критичний клас оминає ВСІ тихі години та користувацький opt-out
    if (event.severity === Severity.CRITICAL) {
      return { deliver: true, forceDigest: false };
    }

    // Перевірка явного Opt-Out користувача на дану категорію евенту
    if (pref.optedOutTypes.has(event.eventType)) {
      return { deliver: false, forceDigest: false };
    }

    // Розрахунок попадання у вікно Quiet Hours з урахуванням переходу через північ
    const inQuietHours = pref.quietHoursStart > pref.quietHoursEnd
      ? (currentHour >= pref.quietHoursStart || currentHour < pref.quietHoursEnd)
      : (currentHour >= pref.quietHoursStart && currentHour < pref.quietHoursEnd);

    // Якщо зараз тихі години і користувач ВДОМА (не у режимі Away)
    if (inQuietHours && !pref.isAwayMode) {
      if (event.severity === Severity.LOW || event.severity === Severity.DEFAULT) {
        // Затримуємо подію для злиття в ранковий дайджест
        return { deliver: false, forceDigest: true };
      }
    }

    return { deliver: true, forceDigest: false };
  }
}

/**
 * 2. NotificationRouter — розгортання Fan-out та формування завдань доставки
 */
export class NotificationRouter {
  private policyEngine = new PolicyEngine();

  buildDeliveryTasks(
    event: HomeEvent,
    members: UserPreference[],
    devicesByUser: Map<string, UserDevice[]>,
    currentHour: number
  ): DeliveryTask[] {
    const tasks: DeliveryTask[] = [];

    for (const member of members) {
      const decision = this.policyEngine.shouldDeliver(event, member, currentHour);

      if (!decision.deliver) {
        if (decision.forceDigest) {
          console.log(`[Digest Buffer] Event ${event.eventId} buffered for morning digest of user ${member.userId}`);
        }
        continue;
      }

      const userDevices = devicesByUser.get(member.userId) ?? [];
      for (const device of userDevices) {
        // Формуємо базовий детермінований ідентифікатор для гарантії ідемпотентності
        const rawId = `${event.eventId}:${member.userId}:${device.deviceId}`;
        const baseDeliveryId = createHash("sha256").update(rawId).digest("hex").slice(0, 16);

        if (event.severity === Severity.CRITICAL) {
          // Двоточковий імпульс 1: Silent Push для передзавантаження кадрів відео у кеш
          tasks.push({
            deliveryId: `${baseDeliveryId}:silent`,
            eventId: event.eventId,
            userId: member.userId,
            deviceId: device.deviceId,
            channel: ChannelType.SILENT_PUSH,
            title: "",
            body: "",
            tokenOrNumber: device.pushToken,
            attempts: 0,
          });

          // Двоточковий імпульс 2: Critical Alert Push зі звуком і банером
          tasks.push({
            deliveryId: `${baseDeliveryId}:critical`,
            eventId: event.eventId,
            userId: member.userId,
            deviceId: device.deviceId,
            channel: ChannelType.CRITICAL_PUSH,
            title: `🚨 ${event.title}`,
            body: event.body,
            tokenOrNumber: device.pushToken,
            attempts: 0,
          });
        } else {
          // Звичайне push-сповіщення
          tasks.push({
            deliveryId: `${baseDeliveryId}:primary`,
            eventId: event.eventId,
            userId: member.userId,
            deviceId: device.deviceId,
            channel: ChannelType.CRITICAL_PUSH,
            title: event.title,
            body: event.body,
            tokenOrNumber: device.pushToken,
            attempts: 0,
          });
        }
      }
    }

    return tasks;
  }
}

/**
 * 3. DeliveryTracker — виконання доставки та аварійний канальний fallback
 */
export class DeliveryTracker {
  async executeTaskWithFallback(
    task: DeliveryTask,
    sendPushApi: (t: DeliveryTask) => Promise<boolean>,
    sendSmsApi: (number: string, text: string) => Promise<boolean>
  ): Promise<boolean> {
    try {
      const success = await sendPushApi(task);
      if (success) {
        console.log(`[ACK Success] Task ${task.deliveryId} delivered via ${task.channel}`);
        return true;
      }
    } catch (err) {
      console.warn(`[Primary Channel Error] Task ${task.deliveryId}: ${err}`);
    }

    // Автоматичний канальний fallback у SMS для критичних тривог при відсутності ACK
    if (task.channel === ChannelType.CRITICAL_PUSH && task.tokenOrNumber) {
      console.log(`[Escalating] Primary push failed for task ${task.deliveryId}. Attempting SMS fallback...`);
      try {
        const smsSuccess = await sendSmsApi(task.tokenOrNumber, `${task.title}: ${task.body}`);
        if (smsSuccess) {
          console.log(`[Fallback Success] Task ${task.deliveryId} delivered via SMS`);
          return true;
        }
      } catch (smsErr) {
        console.error(`[SMS Channel Error] Task ${task.deliveryId}: ${smsErr}`);
      }
    }

    console.error(`[DLQ Route] Task ${task.deliveryId} failed on all channels. Moving to Dead-Letter Queue.`);
    return false;
  }
}
