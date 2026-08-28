const sys = makeSystem();
const count = (t: string) => sys.db.table(t).length;

// notify ще в базі-дефолті — сповіщення осідає в таблиці jobs:
sys.enqueue({ cls: "notify", key: "notify:smoke-1", payload: { kind: "smoke" } });
console.log("notify ДО випуску   → jobs у базі:", count("jobs"),
            " брокер notify:", sys.broker.depth("notify"));

sys.route.notify = sys.broker;   // ← ЄДИНА правка; жоден виклик enqueue не чіпаємо

// той САМИЙ виклик — тепер їде брокером:
sys.enqueue({ cls: "notify", key: "notify:smoke-2", payload: { kind: "smoke" } });
console.log("notify ПІСЛЯ випуску → jobs у базі:", count("jobs"),
            " брокер notify:", sys.broker.depth("notify"));
