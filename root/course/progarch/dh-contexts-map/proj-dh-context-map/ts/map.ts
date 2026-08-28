// map.ts — ЄДИНЕ джерело правди про межі DH. З нього живуть і ворота, і картинка, і легенда.
type Kind =
  | "partnership"         // рівні, релізяться разом (двобічне)
  | "customer-supplier"   // верховий диктує модель, низовий має голос
  | "conformist"          // приймаємо чужу мову як є
  | "published-language"  // нейтральна подія у спільній шині
  | "shared-kernel"       // крихітне спільне ядро
  | "separate-ways"       // свідомо без стику
  | "acl";                // антикорупційний шар до чужого (за межами репо)

interface Context {
  root: string;                    // де контекст живе у файловій системі
  pub: string;                     // ЄДИНА поверхня, видима іншим контекстам
  allow: Record<string, Kind>;     // кого цей контекст сміє ІМПОРТУВАТИ (доменні ребра)
  open?: boolean;                  // його pub сміють читати ВСІ (ідентичність, шина, ядро)
  kind?: Kind;                     // вид зв'язку для open-вершини
  isolated?: boolean;              // окремі шляхи: у нього не сміє входити НІХТО
}

// Увага: allow — це напрямок ІМПОРТУ (хто кого тягне), а НЕ напрямок течії з таблиці.
// Замовник (низовий) імпортує постачальника (верхового) — тож ребро в даних
// протилежне стрілці на картинці. Про цю пастку — окремо наприкінці.
export const MAP: Record<string, Context> = {
  hub:           { root: "src/hub",           pub: "src/hub/published",
                   allow: { twin: "partnership" } },
  twin:          { root: "src/twin",          pub: "src/twin/published",
                   allow: { hub: "partnership", control: "customer-supplier" } },
  control:       { root: "src/control",       pub: "src/control/published",
                   allow: {} },                       // ядро моделі: імпортує НІКОГО, лише публікує
  automations:   { root: "src/automations",   pub: "src/automations/published",
                   allow: { twin: "customer-supplier" } },
  billing:       { root: "src/billing",       pub: "src/billing/published",
                   allow: { control: "customer-supplier" } },   // споживає published control, не домен
  telemetry:     { root: "src/telemetry",     pub: "src/telemetry/published",
                   allow: {} },                       // годується лише з шини подій (open нижче)
  notifications: { root: "src/notifications", pub: "src/notifications/published",
                   allow: {} },
  video:         { root: "src/video",         pub: "src/video/published",
                   allow: {}, isolated: true },       // окремі шляхи: тільки ідентичність
  identity:      { root: "src/identity",      pub: "src/identity/published",
                   allow: {}, open: true, kind: "conformist" },
  events:        { root: "src/events",        pub: "src/events",            // уся шина — опубл. мова
                   allow: {}, open: true, kind: "published-language" },
  ids:           { root: "src/shared/ids",    pub: "src/shared/ids",        // усе ядро — самі типи
                   allow: {}, open: true, kind: "shared-kernel" },
};
