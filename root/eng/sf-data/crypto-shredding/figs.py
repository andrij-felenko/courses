import os
import sys

# Directory setup
TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(TOPIC_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

# ── 1. worm-vs-crypto-shredding.svg ──────────────────────────────────────────
# Dimensions: 960 x 440
svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .panel-left { fill: #111827; stroke: #ef4444; stroke-width: 1.5; rx: 8px; }
  .panel-right { fill: #111827; stroke: #10b981; stroke-width: 1.5; rx: 8px; }
  .hdr-left { fill: #450a0a; stroke: #ef4444; stroke-width: 1; rx: 6px; }
  .hdr-right { fill: #064e3b; stroke: #10b981; stroke-width: 1; rx: 6px; }
  .card-dark { fill: #1f2937; stroke: #374151; stroke-width: 1; rx: 6px; }
  .card-fail { fill: #371b1b; stroke: #7f1d1d; stroke-width: 1; rx: 6px; }
  .card-pass { fill: #063726; stroke: #065f46; stroke-width: 1; rx: 6px; }
  .badge-red { fill: #7f1d1d; stroke: #ef4444; stroke-width: 1; rx: 4px; }
  .badge-green { fill: #064e3b; stroke: #10b981; stroke-width: 1; rx: 4px; }
  .txt { fill: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-title { fill: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 17px; font-weight: bold; }
  .txt-hdr { fill: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-bold { fill: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; }
  .txt-mono { fill: #e5e7eb; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; }
  .txt-muted { fill: #9ca3af; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-danger { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-success { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow-fail { stroke: #ef4444; stroke-width: 2; stroke-dasharray: 4; fill: none; marker-end: url(#arr-red); }
  .arrow-pass { stroke: #10b981; stroke-width: 2; fill: none; marker-end: url(#arr-green); }
</style>
<defs>
  <marker id="arr-red" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#ef4444" />
  </marker>
  <marker id="arr-green" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#10b981" />
  </marker>
</defs>

<rect width="960" height="440" class="bg" />
<text x="30" y="32" class="txt-title">Фізичне стирання проти криптографічного знищення (Crypto-shredding)</text>
<text x="30" y="52" class="txt-muted">Конфлікт між незмінністю носіїв (WORM, бекапи, розподілені логи) та видаленням окремих записів</text>

<!-- Ліва колонка: Проблема фізичного стирання -->
<rect x="30" y="75" width="435" height="340" class="panel-left" />
<rect x="42" y="87" width="411" height="34" class="hdr-left" />
<text x="56" y="109" class="txt-hdr" fill="#fca5a5">Фізичне стирання: неможливе або руйнівне</text>

<rect x="45" y="133" width="405" height="60" class="card-dark" />
<text x="57" y="153" class="txt-bold">Незмінні WORM-сховища (S3 Object Lock):</text>
<text x="57" y="171" class="txt-muted">Режим Compliance блокує зміну об'єктів на 7 років</text>
<text x="57" y="186" class="txt-danger">Помилка S3: 403 AccessDenied (Object is locked)</text>

<rect x="45" y="201" width="405" height="60" class="card-dark" />
<text x="57" y="221" class="txt-bold">Колосальне посилення запису (Write Amplification):</text>
<text x="57" y="239" class="txt-muted">Перезапис одного рядка вимагає перезбирання 50 ТБ Parquet</text>
<text x="57" y="254" class="txt-danger">Витрати: тисячі доларів I/O та збої реплікації</text>

<rect x="45" y="269" width="405" height="60" class="card-dark" />
<text x="57" y="289" class="txt-bold">Стрічкові архіви (LTO) та холодні бекапи:</text>
<text x="57" y="307" class="txt-muted">Дані фізично записані на магнітній стрічці офлайн</text>
<text x="57" y="322" class="txt-danger">Неможливо модифікувати без повної перезаписи касети</text>

<rect x="45" y="337" width="405" height="66" class="card-fail" />
<text x="57" y="359" class="txt-danger">Підсумок: Архітектурний глухий кут</text>
<text x="57" y="377" class="txt-muted">Фізичне стирання порушує комплаєнс або є економічно</text>
<text x="57" y="393" class="txt-muted">неможливим у розподілених незмінних системах</text>

<!-- Права колонка: Crypto-shredding -->
<rect x="495" y="75" width="435" height="340" class="panel-right" />
<rect x="507" y="87" width="411" height="34" class="hdr-right" />
<text x="521" y="109" class="txt-hdr" fill="#86efac">Crypto-shredding: математичне знищення</text>

<rect x="510" y="133" width="405" height="60" class="card-dark" />
<text x="522" y="153" class="txt-bold">Індивідуальний ключ шифрування (DEK):</text>
<text x="522" y="171" class="txt-muted">Кожен користувач/об'єкт шифрується ключем AES-256</text>
<text x="522" y="186" class="txt-success">Дані у сховищі WORM лежать у вигляді шифротексту</text>

<rect x="510" y="201" width="405" height="60" class="card-dark" />
<text x="522" y="221" class="txt-bold">Знищення 32-байтного ключа замість терабайтів:</text>
<text x="522" y="239" class="txt-muted">Видалення ключа DEK із KMS/каталогу за 1 мілісекунду</text>
<text x="522" y="254" class="txt-success">Операція O(1) за часом та дисковим навантаженням</text>

<rect x="510" y="269" width="405" height="60" class="card-dark" />
<text x="522" y="289" class="txt-bold">Математична незворотність (IND-CCA2):</text>
<text x="522" y="307" class="txt-muted">Шифротекст стає невідрізненним від випадкового білого шуму</text>
<text x="522" y="322" class="txt-success">Складність підбору ключа: 2^256 операцій (нездоланно)</text>

<rect x="510" y="337" width="405" height="66" class="card-pass" />
<text x="522" y="359" class="txt-success">Підсумок: Повна відповідність GDPR / NIST SP 800-88</text>
<text x="522" y="377" class="txt-muted">Незмінні сховища залишаються цілісними, а персональні</text>
<text x="522" y="393" class="txt-muted">дані безповоротно й гарантовано знищені для всіх копій</text>
</svg>
"""

# ── 2. envelope-key-hierarchy.svg ────────────────────────────────────────────
# Dimensions: 960 x 420
svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 420" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .kms-box { fill: #1e1b4b; stroke: #6366f1; stroke-width: 1.5; rx: 8px; }
  .app-box { fill: #0f172a; stroke: #38bdf8; stroke-width: 1.5; rx: 8px; }
  .store-box { fill: #18181b; stroke: #a1a1aa; stroke-width: 1.5; rx: 8px; }
  .card-kek { fill: #312e81; stroke: #818cf8; stroke-width: 1; rx: 6px; }
  .card-dek { fill: #064e3b; stroke: #34d399; stroke-width: 1; rx: 6px; }
  .card-edek { fill: #451a03; stroke: #f59e0b; stroke-width: 1; rx: 6px; }
  .card-cipher { fill: #27272a; stroke: #71717a; stroke-width: 1; rx: 6px; }
  .txt { fill: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-title { fill: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 17px; font-weight: bold; }
  .txt-hdr { fill: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-bold { fill: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; }
  .txt-mono { fill: #e5e7eb; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; }
  .txt-muted { fill: #9ca3af; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-indigo { fill: #a5b4fc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-emerald { fill: #6ee7b7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-amber { fill: #fcd34d; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow { stroke: #94a3b8; stroke-width: 1.8; fill: none; marker-end: url(#arr); }
  .arrow-indigo { stroke: #818cf8; stroke-width: 1.8; fill: none; marker-end: url(#arr-indigo); }
  .arrow-emerald { stroke: #34d399; stroke-width: 1.8; fill: none; marker-end: url(#arr-emerald); }
</style>
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#94a3b8" />
  </marker>
  <marker id="arr-indigo" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#818cf8" />
  </marker>
  <marker id="arr-emerald" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#34d399" />
  </marker>
</defs>

<rect width="960" height="420" class="bg" />
<text x="30" y="32" class="txt-title">Ієрархія ключів конвертного шифрування (Envelope Encryption)</text>
<text x="30" y="52" class="txt-muted">Розділення KEK (управління та захист) і DEK (шифрування конкретних даних суб'єкта)</text>

<!-- Рівень 1: KMS / HSM (Зберігання KEK) -->
<rect x="30" y="75" width="270" height="320" class="kms-box" />
<text x="45" y="102" class="txt-hdr" fill="#c7d2fe">KMS / HSM (Апаратний захист)</text>
<text x="45" y="122" class="txt-muted">Ніколи не експортує відкритий KEK</text>

<rect x="45" y="140" width="240" height="85" class="card-kek" />
<text x="55" y="162" class="txt-bold">KEK (Key Encryption Key)</text>
<text x="55" y="180" class="txt-mono">AES-256 / RSA-4096 Master</text>
<text x="55" y="200" class="txt-indigo">Огортає та розгортає DEK</text>

<rect x="45" y="240" width="240" height="135" class="card-kek" />
<text x="55" y="262" class="txt-bold">Операції KMS API:</text>
<text x="55" y="285" class="txt-mono">1. GenerateDataKey(KEK)</text>
<text x="55" y="305" class="txt-mono">   -&gt; Plaintext DEK + EDEK</text>
<text x="55" y="335" class="txt-mono">2. Decrypt(KEK, EDEK)</text>
<text x="55" y="355" class="txt-mono">   -&gt; Plaintext DEK</text>

<!-- Рівень 2: Додаток / RAM (Шифрування) -->
<rect x="340" y="75" width="280" height="320" class="app-box" />
<text x="355" y="102" class="txt-hdr" fill="#7dd3fc">Оперативна пам'ять сервісу (RAM)</text>
<text x="355" y="122" class="txt-muted">Короткоживучі відкриті ключі</text>

<rect x="355" y="140" width="250" height="95" class="card-dek" />
<text x="365" y="162" class="txt-bold">DEK (Data Encryption Key)</text>
<text x="365" y="180" class="txt-mono">AES-256-GCM (32 байти)</text>
<text x="365" y="200" class="txt-emerald">Унікальний на User/Tenant</text>
<text x="365" y="220" class="txt-muted">Scrub via OPENSSL_cleanse</text>

<rect x="355" y="250" width="250" height="125" class="card-dek" />
<text x="365" y="272" class="txt-bold">Шифрування PII payload:</text>
<text x="365" y="295" class="txt-mono">Nonce (12B) + Plaintext</text>
<text x="365" y="315" class="txt-mono">-&gt; AES_GCM_Encrypt(DEK)</text>
<text x="365" y="335" class="txt-mono">-&gt; Ciphertext + Tag (16B)</text>
<text x="365" y="355" class="txt-emerald">Швидкість AES-NI: &gt;5 ГБ/с</text>

<!-- Рівень 3: Сховище (База даних, S3, WORM) -->
<rect x="660" y="75" width="270" height="320" class="store-box" />
<text x="675" y="102" class="txt-hdr" fill="#e4e4e7">Дискове сховище / WORM</text>
<text x="675" y="122" class="txt-muted">Відкриті ключі сюди не потрапляють</text>

<rect x="675" y="140" width="240" height="95" class="card-edek" />
<text x="685" y="162" class="txt-bold">Зашифрований DEK (EDEK)</text>
<text x="685" y="180" class="txt-mono">Ciphertext of DEK (48B)</text>
<text x="685" y="200" class="txt-amber">Зберігається в каталозі ключів</text>
<text x="685" y="220" class="txt-muted">або поруч із даними</text>

<rect x="675" y="250" width="240" height="125" class="card-cipher" />
<text x="685" y="272" class="txt-bold">Зашифровані записи (WORM):</text>
<text x="685" y="295" class="txt-mono">record_id: 1048576</text>
<text x="685" y="315" class="txt-mono">nonce: 0x4f1a8c9e...</text>
<text x="685" y="335" class="txt-mono">payload: 0x9b32e1...</text>
<text x="685" y="355" class="txt-mono">auth_tag: 0x7c4e2a...</text>

<!-- Стрілки зв'язку -->
<path d="M 300 280 L 340 280" class="arrow-indigo" />
<path d="M 605 180 L 660 180" class="arrow-emerald" />
<path d="M 605 310 L 660 310" class="arrow-emerald" />
</svg>
"""

# ── 3. shredding-lifecycle-flow.svg ──────────────────────────────────────────
# Dimensions: 960 x 440
svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" width="100%" height="100%">
<style>
  .bg { fill: #0b0f19; rx: 12px; }
  .step-box { fill: #111827; stroke: #374151; stroke-width: 1.5; rx: 8px; }
  .step-active { fill: #064e3b; stroke: #10b981; stroke-width: 1; rx: 6px; }
  .step-delete { fill: #450a0a; stroke: #ef4444; stroke-width: 1; rx: 6px; }
  .step-shredded { fill: #1e1b4b; stroke: #818cf8; stroke-width: 1; rx: 6px; }
  .card-inner { fill: #1f2937; stroke: #374151; stroke-width: 1; rx: 6px; }
  .txt { fill: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
  .txt-title { fill: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 17px; font-weight: bold; }
  .txt-hdr { fill: #f9fafb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; }
  .txt-bold { fill: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: bold; }
  .txt-mono { fill: #e5e7eb; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; }
  .txt-muted { fill: #9ca3af; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; }
  .txt-danger { fill: #f87171; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .txt-success { fill: #34d399; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: bold; }
  .arrow { stroke: #60a5fa; stroke-width: 2; fill: none; marker-end: url(#arr-blue); }
</style>
<defs>
  <marker id="arr-blue" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#60a5fa" />
  </marker>
</defs>

<rect width="960" height="440" class="bg" />
<text x="30" y="32" class="txt-title">Життєвий цикл та фази Crypto-shredding</text>
<text x="30" y="52" class="txt-muted">Від штатної обробки зашифрованих записів до миттєвої інвалідації та незворотного стану</text>

<!-- Фаза 1: Штатна робота (Active) -->
<rect x="30" y="75" width="280" height="340" class="step-box" />
<rect x="42" y="87" width="256" height="34" class="step-active" />
<text x="54" y="109" class="txt-hdr" fill="#a7f3d0">1. Активний стан (Active)</text>

<rect x="45" y="133" width="250" height="85" class="card-inner" />
<text x="55" y="153" class="txt-bold">Каталог ключів / KMS:</text>
<text x="55" y="173" class="txt-mono">user_id=42 -&gt; EDEK_42</text>
<text x="55" y="195" class="txt-success">Статус: VALID / ACTIVE</text>

<rect x="45" y="230" width="250" height="85" class="card-inner" />
<text x="55" y="250" class="txt-bold">Пам'ять вузлів (Cache):</text>
<text x="55" y="270" class="txt-mono">DEK_42 в кеші LRU</text>
<text x="55" y="292" class="txt-success">Читання/запис без затримок</text>

<rect x="45" y="327" width="250" height="75" class="card-inner" />
<text x="55" y="347" class="txt-bold">Сховище WORM / бекапи:</text>
<text x="55" y="367" class="txt-mono">Ciphertext + Tag валідні</text>
<text x="55" y="387" class="txt-muted">Розшифрування успішне</text>

<!-- Стрілка 1 -> 2 -->
<path d="M 315 240 L 345 240" class="arrow" />

<!-- Фаза 2: Операція стирання (Shredding Action) -->
<rect x="350" y="75" width="260" height="340" class="step-box" />
<rect x="362" y="87" width="236" height="34" class="step-delete" />
<text x="374" y="109" class="txt-hdr" fill="#fca5a5">2. Знищення ключа</text>

<rect x="365" y="133" width="230" height="85" class="card-inner" />
<text x="375" y="153" class="txt-bold">Крок A: Видалення з KMS</text>
<text x="375" y="173" class="txt-mono">DELETE /keys/user_42</text>
<text x="375" y="195" class="txt-danger">EDEK стерто назавжди</text>

<rect x="365" y="230" width="230" height="85" class="card-inner" />
<text x="375" y="250" class="txt-bold">Крок B: Очищення пам'яті</text>
<text x="375" y="270" class="txt-mono">OPENSSL_cleanse(dek)</text>
<text x="375" y="292" class="txt-danger">Інвалідація шини кешу</text>

<rect x="365" y="327" width="230" height="75" class="card-inner" />
<text x="375" y="347" class="txt-bold">Крок C: Аудит-лог</text>
<text x="375" y="367" class="txt-mono">Cert of Erasure: OK</text>
<text x="375" y="387" class="txt-muted">Час операції &lt; 5 мс</text>

<!-- Стрілка 2 -> 3 -->
<path d="M 615 240 L 645 240" class="arrow" />

<!-- Фаза 3: Безповоротний стан (Shredded) -->
<rect x="650" y="75" width="280" height="340" class="step-box" />
<rect x="662" y="87" width="256" height="34" class="step-shredded" />
<text x="674" y="109" class="txt-hdr" fill="#c7d2fe">3. Знищений стан</text>

<rect x="665" y="133" width="250" height="85" class="card-inner" />
<text x="675" y="153" class="txt-bold">Спроба розшифрування:</text>
<text x="675" y="173" class="txt-mono">KMS Error: KeyNotFound</text>
<text x="675" y="195" class="txt-danger">Ключа більше не існує</text>

<rect x="665" y="230" width="250" height="85" class="card-inner" />
<text x="675" y="250" class="txt-bold">Спроба прямої розшифровки:</text>
<text x="675" y="270" class="txt-mono">AES-GCM AuthTag Fail</text>
<text x="675" y="292" class="txt-danger">Помилка автентифікації</text>

<rect x="665" y="327" width="250" height="75" class="card-inner" />
<text x="675" y="347" class="txt-bold">Стан носія (WORM/LTO):</text>
<text x="675" y="367" class="txt-mono">Шифротекст = білий шум</text>
<text x="675" y="387" class="txt-success">Дані юридично стерті</text>
</svg>
"""

# Save SVGs
files = {
    "worm-vs-crypto-shredding.svg": svg1,
    "envelope-key-hierarchy.svg": svg2,
    "shredding-lifecycle-flow.svg": svg3,
}

for name, content in files.items():
    p = os.path.join(IMG_DIR, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {name}")

if __name__ == "__main__":
    print("All figures generated successfully.")
