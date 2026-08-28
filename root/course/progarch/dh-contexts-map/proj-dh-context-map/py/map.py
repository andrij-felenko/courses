# map.py — ЄДИНЕ джерело правди про межі DH. З нього живуть ворота, картинка й легенда.
# Види зв'язку: partnership | customer-supplier | conformist |
#               published-language | shared-kernel | separate-ways | acl
#
# allow — напрямок ІМПОРТУ (хто кого тягне), а НЕ напрямок течії з таблиці:
# замовник (низовий) імпортує постачальника (верхового), тож ребро в даних
# протилежне стрілці на картинці. Про цю пастку — окремо наприкінці.
MAP = {
    "hub":           {"root": "src/hub",           "pub": "src/hub/published",
                      "allow": {"twin": "partnership"}},
    "twin":          {"root": "src/twin",          "pub": "src/twin/published",
                      "allow": {"hub": "partnership", "control": "customer-supplier"}},
    "control":       {"root": "src/control",       "pub": "src/control/published",
                      "allow": {}},                    # ядро: імпортує нікого, лише публікує
    "automations":   {"root": "src/automations",   "pub": "src/automations/published",
                      "allow": {"twin": "customer-supplier"}},
    "billing":       {"root": "src/billing",       "pub": "src/billing/published",
                      "allow": {"control": "customer-supplier"}},  # published control, не домен
    "telemetry":     {"root": "src/telemetry",     "pub": "src/telemetry/published",
                      "allow": {}},                    # годується лише з шини (open нижче)
    "notifications": {"root": "src/notifications", "pub": "src/notifications/published",
                      "allow": {}},
    "video":         {"root": "src/video",         "pub": "src/video/published",
                      "allow": {}, "isolated": True},  # окремі шляхи: тільки ідентичність
    "identity":      {"root": "src/identity",      "pub": "src/identity/published",
                      "allow": {}, "open": True, "kind": "conformist"},
    "events":        {"root": "src/events",        "pub": "src/events",          # уся шина — опубл. мова
                      "allow": {}, "open": True, "kind": "published-language"},
    "ids":           {"root": "src/shared/ids",    "pub": "src/shared/ids",      # усе ядро — самі типи
                      "allow": {}, "open": True, "kind": "shared-kernel"},
}
