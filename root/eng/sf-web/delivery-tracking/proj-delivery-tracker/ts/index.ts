// TypeScript: Production Delivery Tracker & Cascade Fallback Router

export enum DeliveryStatus {
  Created = 'CREATED',
  Dispatched = 'DISPATCHED',
  Sent = 'SENT',
  Delivered = 'DELIVERED',
  Opened = 'OPENED',
  FailedTransient = 'FAILED_TRANSIENT',
  FailedPermanent = 'FAILED_PERMANENT',
  Expired = 'EXPIRED',
}

export enum ChannelType {
  Push = 'PUSH',
  Sms = 'SMS',
  Email = 'EMAIL',
}

const STATUS_RANK: Record<DeliveryStatus, number> = {
  [DeliveryStatus.Created]: 0,
  [DeliveryStatus.Dispatched]: 1,
  [DeliveryStatus.Sent]: 2,
  [DeliveryStatus.Delivered]: 3,
  [DeliveryStatus.Opened]: 4,
  [DeliveryStatus.FailedTransient]: -1,
  [DeliveryStatus.FailedPermanent]: -2,
  [DeliveryStatus.Expired]: -3,
};

export interface NotificationAttempt {
  attemptId: string;
  channel: ChannelType;
  provider: string;
  providerMessageId?: string;
  status: DeliveryStatus;
  errorCode?: string;
  dispatchedAt: number;
  updatedAt: number;
}

export interface NotificationEnvelope {
  id: string;
  userId: string;
  priority: 'HIGH' | 'NORMAL';
  payload: {
    title: string;
    body: string;
    actionUrl?: string;
  };
  currentStatus: DeliveryStatus;
  currentChannelIndex: number;
  channelCascade: ChannelType[];
  timeoutSecondsPerChannel: number[];
  createdAt: number;
  expiresAt: number;
  attempts: NotificationAttempt[];
  fallbackTimerHandle?: NodeJS.Timeout;
}

export interface DsnWebhookPayload {
  eventId: string;
  provider: string;
  providerMessageId: string;
  notificationId: string;
  status: DeliveryStatus;
  errorCode?: string;
  timestamp: number;
}

export interface DeliveryGateway {
  send(
    notificationId: string,
    channel: ChannelType,
    payload: { title: string; body: string }
  ): Promise<{ success: boolean; providerMessageId?: string; errorCode?: string; isPermanent: boolean }>;
}

export class DeliveryTrackerService {
  private notifications: Map<string, NotificationEnvelope> = new Map();
  private processedWebhookEvents: Set<string> = new Set();
  private gateway: DeliveryGateway;

  constructor(gateway: DeliveryGateway) {
    this.gateway = gateway;
  }

  public async submitNotification(
    id: string,
    userId: string,
    payload: { title: string; body: string; actionUrl?: string },
    ttlSeconds: number = 300,
    cascade: ChannelType[] = [ChannelType.Push, ChannelType.Sms, ChannelType.Email],
    timeouts: number[] = [45, 60, 120]
  ): Promise<NotificationEnvelope> {
    const now = Date.now();
    const envelope: NotificationEnvelope = {
      id,
      userId,
      priority: 'HIGH',
      payload,
      currentStatus: DeliveryStatus.Created,
      currentChannelIndex: 0,
      channelCascade: cascade,
      timeoutSecondsPerChannel: timeouts,
      createdAt: now,
      expiresAt: now + ttlSeconds * 1000,
      attempts: [],
    };

    this.notifications.set(id, envelope);
    await this.executeCascadeStep(envelope);
    return envelope;
  }

  private async executeCascadeStep(envelope: NotificationEnvelope): Promise<void> {
    const now = Date.now();

    if (now >= envelope.expiresAt) {
      this.updateStateMonotonic(envelope, DeliveryStatus.Expired, 'TTL elapsed before delivery');
      this.clearFallbackTimer(envelope);
      return;
    }

    if (envelope.currentChannelIndex >= envelope.channelCascade.length) {
      this.updateStateMonotonic(envelope, DeliveryStatus.FailedPermanent, 'All fallback channels exhausted');
      this.clearFallbackTimer(envelope);
      return;
    }

    const currentChannel = envelope.channelCascade[envelope.currentChannelIndex];
    const timeoutSec = envelope.timeoutSecondsPerChannel[envelope.currentChannelIndex] || 60;

    const attempt: NotificationAttempt = {
      attemptId: `att_${envelope.id}_${envelope.currentChannelIndex + 1}`,
      channel: currentChannel,
      provider: currentChannel === ChannelType.Push ? 'APNS_FCM' : currentChannel === ChannelType.Sms ? 'TWILIO' : 'AWS_SES',
      status: DeliveryStatus.Dispatched,
      dispatchedAt: now,
      updatedAt: now,
    };
    envelope.attempts.push(attempt);
    this.updateStateMonotonic(envelope, DeliveryStatus.Dispatched);

    this.clearFallbackTimer(envelope);
    envelope.fallbackTimerHandle = setTimeout(() => {
      this.handleFallbackTimeout(envelope.id);
    }, timeoutSec * 1000);

    try {
      const result = await this.gateway.send(envelope.id, currentChannel, envelope.payload);
      attempt.updatedAt = Date.now();

      if (result.success) {
        attempt.providerMessageId = result.providerMessageId;
        attempt.status = DeliveryStatus.Sent;
        this.updateStateMonotonic(envelope, DeliveryStatus.Sent);
      } else {
        attempt.errorCode = result.errorCode;
        if (result.isPermanent) {
          attempt.status = DeliveryStatus.FailedPermanent;
          this.clearFallbackTimer(envelope);
          envelope.currentChannelIndex++;
          await this.executeCascadeStep(envelope);
        } else {
          attempt.status = DeliveryStatus.FailedTransient;
        }
      }
    } catch (err: any) {
      attempt.status = DeliveryStatus.FailedTransient;
      attempt.errorCode = err.message;
      attempt.updatedAt = Date.now();
    }
  }

  private async handleFallbackTimeout(notificationId: string): Promise<void> {
    const envelope = this.notifications.get(notificationId);
    if (!envelope) return;

    if (
      envelope.currentStatus === DeliveryStatus.Delivered ||
      envelope.currentStatus === DeliveryStatus.Opened ||
      envelope.currentStatus === DeliveryStatus.Expired
    ) {
      return;
    }

    envelope.currentChannelIndex++;
    await this.executeCascadeStep(envelope);
  }

  public handleDsnWebhook(webhook: DsnWebhookPayload): { accepted: boolean; reason?: string } {
    if (this.processedWebhookEvents.has(webhook.eventId)) {
      return { accepted: true, reason: 'Duplicate event ignored' };
    }
    this.processedWebhookEvents.add(webhook.eventId);

    const envelope = this.notifications.get(webhook.notificationId);
    if (!envelope) {
      return { accepted: false, reason: 'Notification not found' };
    }

    const attempt = envelope.attempts.find(
      (a) => a.providerMessageId === webhook.providerMessageId || a.channel === envelope.channelCascade[envelope.currentChannelIndex]
    );

    if (attempt) {
      attempt.status = webhook.status;
      attempt.errorCode = webhook.errorCode;
      attempt.updatedAt = Date.now();
    }

    this.updateStateMonotonic(envelope, webhook.status, webhook.errorCode);

    if (webhook.status === DeliveryStatus.Delivered || webhook.status === DeliveryStatus.Opened) {
      this.clearFallbackTimer(envelope);
    }

    return { accepted: true };
  }

  public recordUserOpen(notificationId: string): boolean {
    const envelope = this.notifications.get(notificationId);
    if (!envelope) return false;

    this.clearFallbackTimer(envelope);
    this.updateStateMonotonic(envelope, DeliveryStatus.Opened);
    return true;
  }

  private updateStateMonotonic(
    envelope: NotificationEnvelope,
    newStatus: DeliveryStatus,
    reason?: string
  ): boolean {
    const currentRank = STATUS_RANK[envelope.currentStatus] ?? 0;
    const newRank = STATUS_RANK[newStatus] ?? 0;

    if (newRank < 0) {
      if (currentRank < STATUS_RANK[DeliveryStatus.Delivered]) {
        envelope.currentStatus = newStatus;
        return true;
      }
      return false;
    }

    if (newRank > currentRank) {
      envelope.currentStatus = newStatus;
      return true;
    }

    return false;
  }

  private clearFallbackTimer(envelope: NotificationEnvelope): void {
    if (envelope.fallbackTimerHandle) {
      clearTimeout(envelope.fallbackTimerHandle);
      envelope.fallbackTimerHandle = undefined;
    }
  }

  public getNotification(id: string): NotificationEnvelope | undefined {
    return this.notifications.get(id);
  }
}
