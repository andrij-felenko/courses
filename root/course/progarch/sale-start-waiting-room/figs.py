import os

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def create_svg(filename, width, height, content):
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<style>
    .bg {{ fill: #0d1117; }}
    .box {{ fill: #161b22; stroke: #30363d; stroke-width: 1.5; rx: 8px; }}
    .box-highlight {{ fill: #1c2128; stroke: #58a6ff; stroke-width: 2; rx: 8px; }}
    .box-success {{ fill: #1c2128; stroke: #3fb950; stroke-width: 2; rx: 8px; }}
    .box-warning {{ fill: #1c2128; stroke: #d29922; stroke-width: 2; rx: 8px; }}
    .box-danger {{ fill: #1c2128; stroke: #f85149; stroke-width: 2; rx: 8px; }}
    text {{ font-family: system-ui, -apple-system, sans-serif; }}
    .title {{ font-size: 13px; font-weight: bold; fill: #f0f6fc; }}
    .subtitle {{ font-size: 11px; fill: #8b949e; }}
    .text-sm {{ font-size: 10px; fill: #c9d1d9; }}
    .line {{ stroke: #8b949e; stroke-width: 1.5; fill: none; }}
    .line-blue {{ stroke: #58a6ff; stroke-width: 2; fill: none; }}
    .line-green {{ stroke: #3fb950; stroke-width: 2; fill: none; }}
    .line-orange {{ stroke: #d29922; stroke-width: 2; fill: none; stroke-dasharray: 4 4; }}
    .arrow {{ fill: #8b949e; }}
    .arrow-blue {{ fill: #58a6ff; }}
    .arrow-green {{ fill: #3fb950; }}
</style>
<rect width="100%" height="100%" class="bg"/>
<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" class="arrow"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" class="arrow-blue"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" class="arrow-green"/>
    </marker>
</defs>
{content}
</svg>'''
    with open(os.path.join(IMG_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg_content)

# 1. Architecture diagram
def gen_arch_diagram():
    content = '''
    <text x="500" y="35" class="title" text-anchor="middle">Архітектура згладжування спалаху трафіку за допомогою Virtual Waiting Room</text>

    <!-- Clients / Ingress -->
    <rect x="30" y="70" width="170" height="210" class="box-danger"/>
    <text x="115" y="105" class="title" text-anchor="middle">500,000 користувачів</text>
    <text x="115" y="135" class="subtitle" text-anchor="middle">Спалах трафіку на T=0</text>
    <text x="115" y="165" class="text-sm" text-anchor="middle">500k HTTP GET /buy</text>
    <text x="115" y="195" class="text-sm" text-anchor="middle">Мобільні + Web + Боти</text>
    <text x="115" y="245" class="subtitle" text-anchor="middle" fill="#f85149">100x від ємності Origin</text>

    <!-- Arrow from clients to Edge Gatekeeper -->
    <line x1="200" y1="175" x2="255" y2="175" class="line" marker-end="url(#arrow)"/>
    <text x="227" y="160" class="text-sm" text-anchor="middle">500k rps</text>

    <!-- Edge / CDN Gatekeeper -->
    <rect x="260" y="70" width="240" height="210" class="box-highlight"/>
    <text x="380" y="105" class="title" text-anchor="middle">Edge Gatekeeper (CDN / WAF)</text>
    <text x="380" y="130" class="subtitle" text-anchor="middle">Cloudflare / NGINX / Envoy</text>
    <rect x="275" y="145" width="210" height="40" class="box"/>
    <text x="380" y="170" class="text-sm" text-anchor="middle">HMAC Перевірка Токену</text>
    <rect x="275" y="195" width="210" height="70" class="box"/>
    <text x="380" y="220" class="text-sm" text-anchor="middle">Редирект 302 (без токену)</text>
    <text x="380" y="245" class="text-sm" text-anchor="middle">Пропуск Pass (з токеном)</text>

    <!-- Arrow Redirect to Waiting Room -->
    <path d="M 380 280 L 380 375 L 565 375" class="line-orange" marker-end="url(#arrow)"/>
    <text x="470" y="360" class="text-sm" text-anchor="middle" fill="#d29922">Без токену -&gt; Waiting Room (302)</text>

    <!-- Virtual Waiting Room System -->
    <rect x="575" y="290" width="270" height="160" class="box-warning"/>
    <text x="710" y="320" class="title" text-anchor="middle">Virtual Waiting Room</text>
    <text x="710" y="342" class="subtitle" text-anchor="middle">Статичний CDN + SSE / Polling</text>
    <rect x="595" y="355" width="230" height="38" class="box"/>
    <text x="710" y="379" class="text-sm" text-anchor="middle">Redis Cluster FIFO Queue</text>
    <rect x="595" y="400" width="230" height="38" class="box"/>
    <text x="710" y="424" class="text-sm" text-anchor="middle">Token Issuer (Signed JWT)</text>

    <!-- Arrow from Gatekeeper to Origin -->
    <line x1="500" y1="175" x2="635" y2="175" class="line-green" marker-end="url(#arrow-green)"/>
    <text x="567" y="160" class="text-sm" text-anchor="middle" fill="#3fb950">5,000 rps</text>

    <!-- Protected Origin -->
    <rect x="640" y="70" width="240" height="210" class="box-success"/>
    <text x="760" y="105" class="title" text-anchor="middle">Protected Origin Backend</text>
    <text x="760" y="130" class="subtitle" text-anchor="middle">Сервіс Продажу Квитків</text>
    <rect x="655" y="145" width="210" height="40" class="box"/>
    <text x="760" y="170" class="text-sm" text-anchor="middle">API Gateway / App Cluster</text>
    <rect x="655" y="195" width="210" height="70" class="box"/>
    <text x="760" y="220" class="text-sm" text-anchor="middle">Transactional DB / Lock</text>
    <text x="760" y="245" class="text-sm" text-anchor="middle">Лимитований пропуск</text>

    <!-- Feedback loop: Issued Token -->
    <path d="M 710 290 L 710 250 L 530 250 L 530 215 L 500 215" class="line-blue" marker-end="url(#arrow-blue)"/>
    <text x="620" y="240" class="text-sm" text-anchor="middle" fill="#58a6ff">Pass Token</text>
    '''
    create_svg("waiting-room-architecture.svg", 1000, 480, content)

# 2. Lifecycle state diagram
def gen_lifecycle_diagram():
    content = '''
    <text x="510" y="35" class="title" text-anchor="middle">Життєвий цикл сесії користувача у Virtual Waiting Room</text>

    <!-- State 1: Pre-queue -->
    <rect x="25" y="70" width="185" height="120" class="box"/>
    <text x="117" y="105" class="title" text-anchor="middle">1. Pre-queue</text>
    <text x="117" y="135" class="subtitle" text-anchor="middle">Відлік до початку продажів</text>
    <text x="117" y="165" class="text-sm" text-anchor="middle">Лендинг із таймером</text>

    <line x1="210" y1="130" x2="275" y2="130" class="line" marker-end="url(#arrow)"/>
    <text x="242" y="115" class="text-sm" text-anchor="middle">T = 0</text>

    <!-- State 2: Random Shuffle -->
    <rect x="280" y="70" width="185" height="120" class="box-warning"/>
    <text x="372" y="105" class="title" text-anchor="middle">2. Pre-sale Shuffle</text>
    <text x="372" y="135" class="subtitle" text-anchor="middle">Рандомізація черги</text>
    <text x="372" y="165" class="text-sm" text-anchor="middle">Захист від скриптів</text>

    <line x1="465" y1="130" x2="525" y2="130" class="line" marker-end="url(#arrow)"/>
    <text x="495" y="115" class="text-sm" text-anchor="middle">Позиція</text>

    <!-- State 3: Active Queue -->
    <rect x="530" y="70" width="185" height="120" class="box-highlight"/>
    <text x="622" y="105" class="title" text-anchor="middle">3. Active Queue</text>
    <text x="622" y="135" class="subtitle" text-anchor="middle">Очікування в черзі</text>
    <text x="622" y="165" class="text-sm" text-anchor="middle">SSE / Опитування</text>

    <line x1="715" y1="130" x2="775" y2="130" class="line-green" marker-end="url(#arrow-green)"/>
    <text x="745" y="115" class="text-sm" text-anchor="middle" fill="#3fb950">Допущено</text>

    <!-- State 4: Admitted -->
    <rect x="780" y="70" width="185" height="120" class="box-success"/>
    <text x="872" y="105" class="title" text-anchor="middle">4. Admitted</text>
    <text x="872" y="135" class="subtitle" text-anchor="middle">Отримано Pass Token</text>
    <text x="872" y="165" class="text-sm" text-anchor="middle">Криптографічний HMAC</text>

    <!-- Down arrow to Checkout -->
    <line x1="872" y1="190" x2="872" y2="245" class="line-green" marker-end="url(#arrow-green)"/>
    <text x="885" y="220" class="text-sm" text-anchor="start" fill="#3fb950">Перехід</text>

    <!-- State 5: Checkout Session -->
    <rect x="780" y="250" width="185" height="120" class="box-success"/>
    <text x="872" y="285" class="title" text-anchor="middle">5. Checkout Session</text>
    <text x="872" y="315" class="subtitle" text-anchor="middle">Вибір місця й оплата</text>
    <text x="872" y="345" class="text-sm" text-anchor="middle">Таймер сесії 10 хв</text>

    <!-- Path to Completed -->
    <line x1="780" y1="310" x2="605" y2="310" class="line-green" marker-end="url(#arrow-green)"/>
    <text x="692" y="295" class="text-sm" text-anchor="middle" fill="#3fb950">Оплата успішна</text>

    <rect x="420" y="250" width="185" height="120" class="box"/>
    <text x="512" y="285" class="title" text-anchor="middle">6. Completed</text>
    <text x="512" y="315" class="subtitle" text-anchor="middle">Квиток викуплено</text>
    <text x="512" y="345" class="text-sm" text-anchor="middle">Сесію завершено</text>

    <!-- Path to Timeout Expired -->
    <path d="M 872 370 L 872 430 L 272 430 L 272 370" class="line-orange" marker-end="url(#arrow)"/>
    <text x="572" y="415" class="text-sm" text-anchor="middle" fill="#d29922">Таймаут вибору квитка або оплати</text>

    <rect x="180" y="250" width="185" height="120" class="box-danger"/>
    <text x="272" y="285" class="title" text-anchor="middle">7. Slot Released</text>
    <text x="272" y="315" class="subtitle" text-anchor="middle">Анулювання токену</text>
    <text x="272" y="345" class="text-sm" text-anchor="middle">Слот передано черзі</text>
    '''
    create_svg("queue-state-lifecycle.svg", 1020, 470, content)

# 3. Token validation sequence flow
def gen_token_flow_diagram():
    content = '''
    <text x="490" y="35" class="title" text-anchor="middle">Послідовність перевірки токену доступу на Edge Gatekeeper</text>

    <!-- Columns -->
    <text x="110" y="65" class="subtitle" text-anchor="middle">Клієнт (Браузер)</text>
    <line x1="110" y1="80" x2="110" y2="430" class="line" stroke-dasharray="2 2"/>

    <text x="370" y="65" class="subtitle" text-anchor="middle">Edge Gatekeeper (WAF)</text>
    <line x1="370" y1="80" x2="370" y2="430" class="line" stroke-dasharray="2 2"/>

    <text x="630" y="65" class="subtitle" text-anchor="middle">Waiting Room Service</text>
    <line x1="630" y1="80" x2="630" y2="430" class="line" stroke-dasharray="2 2"/>

    <text x="850" y="65" class="subtitle" text-anchor="middle">Origin Ticket DB</text>
    <line x1="850" y1="80" x2="850" y2="430" class="line" stroke-dasharray="2 2"/>

    <!-- Step 1: Initial Request without token -->
    <line x1="110" y1="105" x2="360" y2="105" class="line" marker-end="url(#arrow)"/>
    <text x="235" y="95" class="text-sm" text-anchor="middle">1. GET /buy/ticket-123 (без токену)</text>

    <!-- Edge check box -->
    <rect x="280" y="118" width="180" height="30" class="box-danger"/>
    <text x="370" y="137" class="text-sm" text-anchor="middle">Токен відсутній!</text>

    <!-- Step 2: Redirect 302 -->
    <line x1="360" y1="170" x2="115" y2="170" class="line-orange" marker-end="url(#arrow)"/>
    <text x="235" y="160" class="text-sm" text-anchor="middle" fill="#d29922">2. HTTP 302 Redirect (queue.domain.com)</text>

    <!-- Step 3: Polling / Waiting -->
    <line x1="110" y1="210" x2="620" y2="210" class="line" marker-end="url(#arrow)"/>
    <text x="365" y="200" class="text-sm" text-anchor="middle">3. SSE / Heartbeat перевірка стану</text>

    <rect x="540" y="225" width="180" height="35" class="box-warning"/>
    <text x="630" y="247" class="text-sm" text-anchor="middle">Черга: Позиція #420</text>

    <!-- Step 4: Admission Token Issuance -->
    <line x1="620" y1="280" x2="115" y2="280" class="line-green" marker-end="url(#arrow-green)"/>
    <text x="365" y="270" class="text-sm" text-anchor="middle" fill="#3fb950">4. Видача Pass Token (HMAC-SHA256)</text>

    <!-- Step 5: Request with Pass Token -->
    <line x1="110" y1="325" x2="360" y2="325" class="line-green" marker-end="url(#arrow-green)"/>
    <text x="235" y="315" class="text-sm" text-anchor="middle" fill="#3fb950">5. GET /buy/ticket-123 + Cookie token</text>

    <!-- Edge HMAC Validation -->
    <rect x="260" y="338" width="220" height="45" class="box-success"/>
    <text x="370" y="357" class="text-sm" text-anchor="middle">6. Валідація HMAC (локальна)</text>
    <text x="370" y="373" class="text-sm" text-anchor="middle">Без виклику Origin DB</text>

    <!-- Step 7: Proxy to Origin -->
    <line x1="380" y1="400" x2="845" y2="400" class="line-green" marker-end="url(#arrow-green)"/>
    <text x="612" y="390" class="text-sm" text-anchor="middle" fill="#3fb950">7. Передача запиту в Origin DB</text>
    '''
    create_svg("token-validation-flow.svg", 980, 470, content)

# 4. Math queue rates chart
def gen_math_rates_diagram():
    content = '''
    <text x="500" y="35" class="title" text-anchor="middle">Динаміка трафіку: Вхідний спалах, Пропуск Origin та Накопичена Черга</text>

    <!-- Axes -->
    <line x1="90" y1="360" x2="900" y2="360" class="line"/>
    <text x="915" y="365" class="text-start">Час t</text>
    <line x1="90" y1="360" x2="90" y2="60" class="line"/>
    <text x="90" y="50" class="title" text-anchor="middle">Запити / сек</text>

    <!-- Grid lines -->
    <line x1="90" y1="90" x2="900" y2="90" stroke="#21262d" stroke-dasharray="2 2"/>
    <text x="80" y="95" class="text-sm" text-anchor="end">500k rps</text>
    <line x1="90" y1="310" x2="900" y2="310" stroke="#21262d" stroke-dasharray="2 2"/>
    <text x="80" y="315" class="text-sm" text-anchor="end">5k rps</text>

    <!-- Incoming burst line -->
    <path d="M 90 340 L 120 90 L 160 170 L 250 270 L 400 330 L 900 335" class="line-orange"/>
    <text x="230" y="80" class="text-sm" text-anchor="middle" fill="#d29922">Спалах λ_in(t) = 500,000 rps</text>

    <!-- Capacity admission rate line -->
    <line x1="90" y1="310" x2="900" y2="310" class="line-green"/>
    <text x="520" y="295" class="text-sm" text-anchor="middle" fill="#3fb950">Лимитований пропуск Origin r(t) = 5,000 rps</text>

    <!-- Accumulated Queue size -->
    <path d="M 120 360 C 200 230, 310 180, 460 190 C 580 200, 720 280, 850 360" class="line-blue"/>
    <text x="460" y="170" class="text-sm" text-anchor="middle" fill="#58a6ff">Накопичена черга Q(t) (макс 450,000 користувачів)</text>

    <!-- Annotations Box in top right, ample margin from y=30 -->
    <rect x="650" y="25" width="250" height="120" class="box"/>
    <text x="775" y="52" class="title" text-anchor="middle">Баланс черги:</text>
    <text x="775" y="76" class="text-sm" text-anchor="middle">Q(t) = ∫ (λ_in(τ) - r(τ)) dτ</text>
    <text x="775" y="98" class="text-sm" text-anchor="middle">Середній час: W = Q(t) / r(t)</text>
    <text x="775" y="120" class="text-sm" text-anchor="middle">W_max = 450,000 / 5,000 = 90 сек</text>
    '''
    create_svg("math-queue-rates.svg", 1000, 420, content)

if __name__ == "__main__":
    gen_arch_diagram()
    gen_lifecycle_diagram()
    gen_token_flow_diagram()
    gen_math_rates_diagram()
    print("All SVGs regenerated successfully.")
