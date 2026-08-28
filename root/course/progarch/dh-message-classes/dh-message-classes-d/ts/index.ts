// Кожен клас трафіку DH — не «повідомлення взагалі», а оголошена форма:
// хто споживає, чи чекають, яка гарантія, чи треба переграти → і звідси канал.
type Intent   = "command" | "document" | "event";       // намір за EIP
type Fanout   = "one-addressed" | "worker-pool" | "many-independent" | "many-unknown";
type Delivery = "effectively-once" | "at-least-once";
type Channel  = "queue" | "work-queue" | "log" | "topic";

interface TrafficClass {
  intent: Intent;
  fanout: Fanout;
  waits: boolean;        // хтось синхронно чекає відповідь?
  delivery: Delivery;
  replayable: boolean;   // чи треба тримати історію й переграти?
  channel: Channel;      // сюди — і тільки сюди — лягає цей клас
}

const DH_TRAFFIC: Record<string, TrafficClass> = {
  deviceCommand: { intent: "command",  fanout: "one-addressed",    waits: true,  delivery: "effectively-once", replayable: false, channel: "queue"      },
  telemetry:     { intent: "document", fanout: "many-independent", waits: false, delivery: "at-least-once",     replayable: true,  channel: "log"        },
  domainEvent:   { intent: "event",    fanout: "many-unknown",     waits: false, delivery: "at-least-once",     replayable: false, channel: "topic"      },
  heavyJob:      { intent: "command",  fanout: "worker-pool",      waits: false, delivery: "at-least-once",     replayable: false, channel: "work-queue" },
};
