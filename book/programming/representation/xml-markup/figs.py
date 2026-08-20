# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F  = "#eef4ff"
RED_F   = "#fdecea"
GREEN_F = "#eaf7ef"
GREY_F  = "#f4f6f8"
WARN_F  = "#fff8e6"
WARN_B  = "#d97706"


# ── 1. infoset-tree: абстрактна модель W3C XML Infoset ─────────────────────────
def fig_infoset_tree():
    W, H = 960, 540
    p = []

    # Ліва колонка: Текстова серіалізація (сирі байти)
    p.append(fitbox(30, 40, 260, 460,
                    "Текстовий потік (XML 1.0)\n\n"
                    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    "<catalog venue=\"Kyiv\">\n"
                    "  <!-- активні товари -->\n"
                    "  <item sku=\"A-102\">\n"
                    "    <title>Sensor</title>\n"
                    "    <price currency=\"UAH\">450</price>\n"
                    "  </item>\n"
                    "</catalog>\n\n"
                    "• Синтаксичні сутності (&lt;, &amp;)\n"
                    "• CDATA секції, пробіли, лапки\n"
                    "• Порядок атрибутів у тексті довільний",
                    size=12, fill=GREY_F, stroke=LINE, sw=1.5))

    # Стрілка перетворення парсером
    p.append(arrow(295, 270, 355, 270, color=NEG, sw=2.5))
    p.append(text(325, 255, "Парсер", size=12, color=NEG, bold=True))

    # Права зона: Ієрархія інформаційних елементів (Infoset Items)
    # Корінь: Document Information Item
    p.append(fitbox(365, 40, 565, 52,
                    "Document Information Item (Корінь документа)\n"
                    "[document element] → catalog, [children], [character encoding scheme] = UTF-8",
                    size=12, fill=BLUE_F, stroke=NEG, sw=2, bold=True))

    # Зв'язок від Document до Root Element
    p.append(arrow(647, 92, 647, 122, color=LINE, sw=1.5))

    # Головний елемент: catalog
    p.append(fitbox(460, 122, 375, 52,
                    "Element Item: <catalog>\n"
                    "[local name] = 'catalog', [namespace name] = null",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True))

    # Атрибут catalog: venue
    p.append(line(460, 148, 380, 148, color=LINE, sw=1.5))
    p.append(fitbox(365, 122, 85, 52,
                    "Attribute Item:\nvenue=\"Kyiv\"",
                    size=11, fill=WARN_F, stroke=WARN_B, sw=1.5))

    # Зв'язок до коментаря і дочірнього елемента item
    p.append(arrow(647, 174, 520, 210, color=LINE, sw=1.5))
    p.append(arrow(647, 174, 720, 210, color=LINE, sw=1.5))

    # Comment Item
    p.append(fitbox(410, 210, 220, 48,
                    "Comment Information Item:\n' активні товари '",
                    size=11, fill=GREY_F, stroke=MUTED, sw=1.2))

    # Element Item: item
    p.append(fitbox(645, 210, 280, 52,
                    "Element Item: <item>\n"
                    "[local name] = 'item', [parent] = catalog",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True))

    # Атрибут item: sku
    p.append(line(785, 262, 785, 285, color=LINE, sw=1.5))
    p.append(fitbox(710, 285, 150, 42,
                    "Attribute Item:\nsku=\"A-102\"",
                    size=11, fill=WARN_F, stroke=WARN_B, sw=1.5))

    # Дочірні елементи item: title та price
    p.append(arrow(680, 262, 490, 355, color=LINE, sw=1.5))
    p.append(arrow(750, 262, 720, 355, color=LINE, sw=1.5))

    # Element Item: title
    p.append(fitbox(390, 355, 200, 50,
                    "Element Item: <title>\n[children] → Character Items",
                    size=11, fill=GREEN_F, stroke=FIELD, sw=1.5))
    p.append(arrow(490, 405, 490, 435, color=LINE, sw=1.5))
    p.append(fitbox(390, 435, 200, 45,
                    "Character Items: [ 'S','e','n','s','o','r' ]\n(послідовність кодів символів)",
                    size=10, fill=BLUE_F, stroke=NEG, sw=1.2))

    # Element Item: price
    p.append(fitbox(620, 355, 200, 50,
                    "Element Item: <price>\n[attributes] → currency",
                    size=11, fill=GREEN_F, stroke=FIELD, sw=1.5))
    p.append(arrow(720, 405, 720, 435, color=LINE, sw=1.5))
    p.append(fitbox(620, 435, 200, 45,
                    "Character Items: [ '4','5','0' ]\n[parent] = price",
                    size=10, fill=BLUE_F, stroke=NEG, sw=1.2))

    # Атрибут currency
    p.append(line(820, 380, 845, 380, color=LINE, sw=1.5))
    p.append(fitbox(845, 355, 105, 50,
                    "Attribute:\ncurrency=\"UAH\"",
                    size=11, fill=WARN_F, stroke=WARN_B, sw=1.5))

    # Легенда
    p.append(fitbox(365, 490, 565, 36,
                    "Легенда:  Зелений = Element Item  |  Жовтий = Attribute Item  |  Синій = Document & Character Items",
                    size=11, fill=BG, stroke=MUTED, sw=1.0, color=MUTED))

    render(os.path.join(OUT, "infoset-tree.svg"), W, H, *p,
           title="Абстрактне дерево W3C XML Information Set")


# ── 2. namespaces-scoping: простори імен, префікси та область видимості ────────
def fig_namespaces_scoping():
    W, H = 960, 520
    p = []

    # Зовнішній контейнер кореня (Scope 1)
    p.append(rect(30, 45, 890, 445, fill=BLUE_F, stroke=NEG, sw=2, rx=8))
    p.append(text(50, 72, "Область видимості кореня: xmlns=\"http://store.org/order\"  |  xmlns:inv=\"http://store.org/inv\"",
                  size=13, color=NEG, anchor="start", bold=True))

    # Вузол order
    p.append(fitbox(50, 90, 390, 70,
                    "Елемент: <order id=\"104\">\n"
                    "• Префікс: немає (Default Namespace)\n"
                    "• Expanded Name: {http://store.org/order, order}\n"
                    "• Атрибут id: {null, id}  (Default NS НЕ діє на атрибути!)",
                    size=11, fill=BG, stroke=NEG, sw=1.5))

    # Розгалуження на дочірній елемент inv:item
    p.append(arrow(245, 160, 245, 195, color=LINE, sw=1.8))

    # Вузол inv:item (всередині кореневого scope)
    p.append(fitbox(50, 195, 390, 68,
                    "Елемент: <inv:item inv:sku=\"TR-88\">\n"
                    "• Префікс: 'inv' → URI 'http://store.org/inv'\n"
                    "• Expanded Name: {http://store.org/inv, item}\n"
                    "• Атрибут inv:sku: {http://store.org/inv, sku}",
                    size=11, fill=BG, stroke=FIELD, sw=1.5))

    # Вкладена область видимості (Scope 2: перевизначення default namespace)
    p.append(rect(470, 90, 430, 280, fill=GREEN_F, stroke=FIELD, sw=2, rx=6))
    p.append(text(485, 115, "Вкладена область: xmlns=\"http://www.w3.org/2000/svg\"",
                  size=12, color=FIELD, anchor="start", bold=True))

    p.append(fitbox(485, 130, 400, 75,
                    "Елемент: <svg width=\"100\" height=\"100\">\n"
                    "• Default NS перекрито на SVG URI!\n"
                    "• Expanded Name: {http://www.w3.org/2000/svg, svg}\n"
                    "• Атрибути width/height: без простору {null, width}",
                    size=11, fill=BG, stroke=FIELD, sw=1.5))

    p.append(arrow(685, 205, 685, 235, color=LINE, sw=1.5))

    p.append(fitbox(485, 235, 400, 65,
                    "Елемент: <circle cx=\"50\" cy=\"50\" r=\"40\"/>\n"
                    "• Успадковує вкладений дефолтний простір SVG\n"
                    "• Expanded Name: {http://www.w3.org/2000/svg, circle}",
                    size=11, fill=BG, stroke=FIELD, sw=1.5))

    p.append(fitbox(485, 310, 400, 50,
                    "Префікс 'inv' все ще доступний з батьківського scope:\n"
                    "<inv:metadata type=\"vector\"/> → {http://store.org/inv, metadata}",
                    size=10.5, fill=WARN_F, stroke=WARN_B, sw=1.2))

    # Зв'язок між лівою та правою частиною
    p.append(arrow(440, 230, 470, 230, color=LINE, sw=1.5))

    # Підсумкове порівняння внизу
    p.append(fitbox(50, 390, 850, 85,
                    "Ключові правила розв'язання XML Namespaces:\n"
                    "1. QName = Prefix ':' LocalPart. Префікс є лише локальним псевдонімом для URI у документі.\n"
                    "2. Елементи без префікса потрапляють у поточний default namespace (xmlns=\"...\").\n"
                    "3. Атрибути без префікса ЗАВЖДИ належать до порожнього простору {null, name}, незалежно від xmlns=\"...\".",
                    size=11.5, fill=BG, stroke=LINE, sw=1.4, bold=False))

    render(os.path.join(OUT, "namespaces-scoping.svg"), W, H, *p,
           title="Область видимості просторів імен та розв'язання QName")


# ── 3. dom-vs-sax-stax: моделі парсингу XML ──────────────────────────────────
def fig_dom_vs_sax_stax():
    W, H = 960, 540
    p = []

    cols = [
        (30, "DOM (Document Object Model)", "Повне дерево у пам'яті", NEG, BLUE_F,
         "Парсер читає весь XML-потік\nі будує повний граф вузлів у купі.\nКожен Node тримає вказівники:\nparent, firstChild, nextSibling,\nатрибути, карти просторів.",
         "Пам'ять: O(N) — у 5–10 разів більше\nза розмір файлу на диску.\nНаприклад: XML 100 МБ → 800 МБ RAM.",
         "✓ Довільний доступ (Random Access)\n✓ XPath, XSLT, модифікація дерева\n✗ Вичерпання RAM на великих файлах"),

        (345, "SAX (Simple API for XML)", "Потоковий push-парсер", FIELD, GREEN_F,
         "Парсер сам крутить цикл читання\nі 'штовхає' події в обробник:\n• startElement(name, attrs)\n• characters(chunk)\n• endElement(name)",
         "Пам'ять: O(1) — фіксований\nбуфер розміром у кілька кілобайтів.\nОбробляє потоки гігабайтного розміру.",
         "✓ Мінімальне споживання RAM\n✗ Зворотне керування (Inversion of Control)\n✗ Складні машини станів (State Machine)"),

        (660, "StAX / XmlReader", "Потоковий pull-парсер", POS, RED_F,
         "Застосунок сам крутить цикл\nі 'витягує' наступний токен:\nwhile (reader.hasNext()) {\n  ev = reader.next();\n  if (ev == START_ELEMENT) ...\n}",
         "Пам'ять: O(1) — фіксований\nбуфер курсора або події.\nКерування потоком у руках клієнта.",
         "✓ Прямий ітератор, чистота коду\n✓ Можливість пропустити піддерево (skip)\n✓ Інтеграція з генераторами/корутинами"),
    ]

    cw = 270
    for x, title, sub, col, fill, how, mem, pros in cols:
        p.append(fitbox(x, 45, cw, 60, title + "\n" + sub, size=13,
                        fill=fill, stroke=col, sw=2.2, bold=True))
        p.append(fitbox(x, 115, cw, 135, "Принцип роботи:\n" + how, size=11,
                        fill=BG, stroke=col, sw=1.4))
        p.append(fitbox(x, 260, cw, 95, "Витрати пам'яті:\n" + mem, size=11,
                        fill=WARN_F, stroke=WARN_B, sw=1.5, bold=True))
        p.append(fitbox(x, 365, cw, 140, "Плюси та мінуси:\n" + pros, size=11,
                        fill=GREY_F, stroke=LINE, sw=1.3))

    render(os.path.join(OUT, "dom-vs-sax-stax.svg"), W, H, *p,
           title="Порівняння архітектур синтаксичного аналізу: DOM, SAX та StAX")


# ── 4. xxe-billion-laughs: вектори атак на XML-парсери ────────────────────────
def fig_xxe_billion_laughs():
    W, H = 960, 520
    p = []

    # Ліва колонка: XXE (XML External Entity Injection)
    p.append(fitbox(30, 45, 435, 60,
                    "XXE: XML External Entity Injection\n"
                    "Зловмисне завантаження зовнішніх ресурсів через DTD",
                    size=13, fill=RED_F, stroke=POS, sw=2, bold=True))

    p.append(fitbox(30, 115, 435, 140,
                    "Payload (шкідливий XML з DTD SYSTEM сутністю):\n\n"
                    "<?xml version=\"1.0\"?>\n"
                    "<!DOCTYPE data [\n"
                    "  <!ENTITY xxe SYSTEM \"file:///etc/passwd\">\n"
                    "]>\n"
                    "<data>&xxe;</data>",
                    size=11.5, fill=GREY_F, stroke=POS, sw=1.4))

    p.append(arrow(247, 255, 247, 285, color=POS, sw=2))

    p.append(fitbox(30, 285, 435, 125,
                    "Наслідки XXE-атаки:\n"
                    "1. Читання довільних локальних файлів сервера (/etc/passwd, конфіги, ключі).\n"
                    "2. Server-Side Request Forgery (SSRF) — сканування внутрішньої мережі.\n"
                    "3. Blind XXE — викрадення даних через DNS/HTTP канали out-of-band.",
                    size=11, fill=WARN_F, stroke=WARN_B, sw=1.5))

    # Права колонка: Billion Laughs (XML Entity Expansion DOS)
    p.append(fitbox(495, 45, 435, 60,
                    "Billion Laughs Attack (XML Bomb)\n"
                    "Експоненційне вичерпання RAM через рекурсивні сутності",
                    size=13, fill=RED_F, stroke=POS, sw=2, bold=True))

    p.append(fitbox(495, 115, 435, 140,
                    "Payload (експоненційне множення сутностей):\n\n"
                    "<!ENTITY lol \"lol\">\n"
                    "<!ENTITY lol1 \"&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;\">\n"
                    "<!ENTITY lol2 \"&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;\">\n"
                    "... <!ENTITY lol9 \"&lol8;&lol8;...\">\n"
                    "<data>&lol9;</data>",
                    size=11, fill=GREY_F, stroke=POS, sw=1.4))

    p.append(arrow(712, 255, 712, 285, color=POS, sw=2))

    p.append(fitbox(495, 285, 435, 125,
                    "Механізм переповнення пам'яті:\n"
                    "• lol1 = 10 · 3 байти = 30 байтів\n"
                    "• lol2 = 10 · 30 = 300 байтів ...\n"
                    "• lol9 = 10⁹ розширень ≈ 3 Гігабайти тексту в пам'яті!\n"
                    "Результат: Heap Exhaustion, падіння процесу через OOM Killer.",
                    size=11, fill=WARN_F, stroke=WARN_B, sw=1.5))

    # Нижній захисний бар'єр
    p.append(fitbox(30, 425, 900, 75,
                    "Методи захисту та загартування парсерів:\n"
                    "• Повне вимкнення DTD: DISALLOW_DOCTYPE_DECL = true (XML_PARSE_NODTD)\n"
                    "• Блокування мережевих сутностей: XML_PARSE_NONET або порожній EntityResolver\n"
                    "• Ліміти розгортання сутностей: обмеження глибини рекурсії та ліміт на обсяг виділеної пам'яті",
                    size=11.5, fill=GREEN_F, stroke=FIELD, sw=2, bold=True))

    render(os.path.join(OUT, "xxe-billion-laughs.svg"), W, H, *p,
           title="Вектори атак на XML-парсери: XXE та експоненційна XML-бомба")


if __name__ == "__main__":
    fig_infoset_tree()
    fig_namespaces_scoping()
    fig_dom_vs_sax_stax()
    fig_xxe_billion_laughs()
    print("All figures generated successfully.")
