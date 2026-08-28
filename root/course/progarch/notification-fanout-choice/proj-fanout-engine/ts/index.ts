interface NotificationEvent {
  id: string;
  title: string;
  body: string;
  scopeId: string;
  recipientCount: number;
  isEmergency: boolean;
}

enum FanOutStrategy {
  FastTrackOnWrite = "FastTrackOnWrite",
  HybridBatched = "HybridBatched",
  BroadcastOnRead = "BroadcastOnRead",
}

interface DispatchDecision {
  strategy: FanOutStrategy;
  batchSize: number;
  routeReason: string;
}

class FanOutRouter {
  private static readonly MAX_DIRECT_ONWRITE = 10;
  private static readonly MAX_COMMUNITY_HYBRID = 5000;
  private static readonly PUSH_BATCH_CHUNK = 500;

  public route(event: NotificationEvent): DispatchDecision {
    if (event.isEmergency || event.recipientCount <= FanOutRouter.MAX_DIRECT_ONWRITE) {
      return {
        strategy: FanOutStrategy.FastTrackOnWrite,
        batchSize: event.recipientCount,
        routeReason: "Tier 1: Аварійний або локальний доступ (N <= 10). Пряма On-Write розсилка.",
      };
    }

    if (event.recipientCount <= FanOutRouter.MAX_COMMUNITY_HYBRID) {
      return {
        strategy: FanOutStrategy.HybridBatched,
        batchSize: FanOutRouter.PUSH_BATCH_CHUNK,
        routeReason: "Tier 2: Подія ЖК (10 < N <= 5000). On-Read стрічка + push-батчі.",
      };
    }

    return {
      strategy: FanOutStrategy.BroadcastOnRead,
      batchSize: 1,
      routeReason: "Tier 3: Системна масова подія (N > 5000). Чистий On-Read + FCM Topic.",
    };
  }

  public executeDispatch(event: NotificationEvent): void {
    const decision = this.route(event);
    console.log(`[ROUTER] Подія ID: ${event.id} | Стратегія: ${decision.strategy} | Опис: ${decision.routeReason}`);

    if (decision.strategy === FanOutStrategy.FastTrackOnWrite) {
      console.log(`  └─ [Tier 1] Запис ${event.recipientCount} персональних inboxes у пам'ять + High-Priority Push.`);
    } else if (decision.strategy === FanOutStrategy.HybridBatched) {
      const numChunks = Math.ceil(event.recipientCount / decision.batchSize);
      console.log(`  └─ [Tier 2] Збережено 1 запис стрічки ЖК ${event.scopeId}. Згенеровано ${numChunks} push-батчів по ${decision.batchSize}.`);
    } else {
      console.log(`  └─ [Tier 3] Збережено 1 глобальний запис у системну стрічку. Multicast push у root://${event.scopeId}`);
    }
  }
}

// Запуск прикладу
const router = new FanOutRouter();
router.executeDispatch({ id: "evt-001", title: "Виявлено дим!", body: "", scopeId: "home-1402", recipientCount: 2, isEmergency: true });
router.executeDispatch({ id: "evt-002", title: "Відключення води", body: "", scopeId: "complex-oak", recipientCount: 1200, isEmergency: false });
router.executeDispatch({ id: "evt-003", title: "Оновлення оферти", body: "", scopeId: "global-dh", recipientCount: 500000, isEmergency: false });
