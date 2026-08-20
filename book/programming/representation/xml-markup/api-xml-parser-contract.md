# 📋 Інтерфейсні контракти XML: Infoset, DOM, SAX та StAX

Цей довідник містить повні специфікації інтерфейсних контрактів, типів даних, сигнатур методів та таблиць властивостей для чотирьох фундаментальних рівнів абстракції XML: моделі інформаційного набору W3C XML Information Set (Infoset), об'єктної моделі документа W3C DOM Core, подієвого потокового інтерфейсу SAX 2.0 та курсорного потокового інтерфейсу StAX (JSR-173) / `XmlReader`.

## 1. W3C XML Information Set (Infoset): базові інформаційні елементи

Модель W3C XML Information Set визначає абстрактний набір даних, який описує зміст коректно сформованого XML-документа незалежно від конкретного синтаксичного запису (використання апострофів чи лапок, порядку атрибутів у тегу або форми запису порожніх елементів). Усі стандартні технології обробки XML (DOM, XPath, XSLT, XML Schema) спираються саме на поняття Information Items (інформаційних елементів) та їхніх іменованих властивостей.

Загалом специфікація W3C Infoset формалізує 11 типів інформаційних елементів:

| Тип інформаційного елемента | Ключові обов'язкові властивості (Properties) | Опис та семантика |
| :--- | :--- | :--- |
| **Document Information Item** | `[document element]`, `[children]`, `[notations]`, `[unparsed entities]`, `[base URI]`, `[character encoding scheme]` | Корінь усього інформаційного набору. Властивість `[document element]` вказує на єдиний кореневий елемент документа. |
| **Element Information Item** | `[namespace name]`, `[local name]`, `[prefix]`, `[children]`, `[attributes]`, `[in-scope namespaces]`, `[base URI]`, `[parent]` | Представляє XML-тег. Властивість `[children]` містить упорядкований список дочірніх елементів, символів, коментарів та інструкцій обробки. |
| **Attribute Information Item** | `[namespace name]`, `[local name]`, `[prefix]`, `[normalized value]`, `[specified]`, `[attribute type]`, `[owner element]` | Представляє пару «ключ-значення» у відкривальному тегу. Властивість `[normalized value]` містить нормалізований текст без зайвих пробілів. |
| **Processing Instruction Item** | `[target]`, `[content]`, `[base URI]`, `[parent]` | Інструкція для зовнішнього застосунку `<?target content?>`. `[target]` визначає цільовий рушій. |
| **Character Information Item** | `[character code]`, `[element content whitespace]`, `[parent]` | Представляє один символ тексту за стандартом Юнікод (ISO/IEC 10646). |
| **Comment Information Item** | `[content]`, `[parent]` | Текстовий коментар `<!-- content -->`. Ігнорується валідаторами схем. |
| **Namespace Information Item** | `[prefix]`, `[namespace name]` | Відображення псевдоніма префікса на глобальний URI простору імен для поточного вузла. |
| **Document Type Declaration** | `[system identifier]`, `[public identifier]`, `[children]`, `[parent]` | Декларація `<!DOCTYPE ...>`, що вказує на граматику DTD та зовнішні схеми. |
| **Unexpanded Entity Item** | `[name]`, `[system identifier]`, `[public identifier]`, `[declaration base URI]` | Посилання на сутність, яку синтаксичний аналізатор не зміг або не став розгортати. |
| **Unparsed Entity Item** | `[name]`, `[system identifier]`, `[public identifier]`, `[notation name]` | Зовнішні бінарні або не-XML дані, задекларовані у DTD. |
| **Notation Information Item** | `[name]`, `[system identifier]`, `[public identifier]`, `[base URI]` | Опис формату непарсованих сутностей або інструкцій обробки. |

### Семантичні інваріанти моделі Infoset

Під час трансляції синтаксичного потоку в абстрактний набір даних діють такі фундаментальні інваріанти:
- **Невпорядкованість атрибутів:** хоча у текстовому файлі атрибути завжди записані в певному порядку, у моделі Infoset властивість `[attributes]` є невпорядкованою множиною. Два документи, що відрізняються лише порядком атрибутів у тегу, породжують ідентичний Infoset.
- **Нормалізація кінців рядків:** послідовності байтів повернення каретки та переведення рядка (`\r\n` або поодинокий `\r`) замінюються на одиничний символ нового рядка `\n` (код Юнікоду `U+000A`).
- **Синтез символьних елементів:** сутності на зразок `&lt;`, `&#60;` або вміст секцій `<![CDATA[<]]>` трансформуються в звичайні об'єкти `Character Information Item` з числовим кодом символу `60` (`<`).

## 2. W3C Document Object Model (DOM Core Level 3)

Об'єктна модель DOM надає стандартизований інтерфейс маніпуляції деревом вузлів у динамічній пам'яті. Кожен вузол реалізує базовий інтерфейс `Node` та спеціалізовані спадкоємці (`Element`, `Attr`, `Text`, `Document`).

### Числові константи типів вузлів (`NodeType`)

Специфікація DOM Level 3 визначає числові ідентифікатори типів вузлів, що повертаються атрибутом `nodeType`:

```
Код   Константа DOM                   Відповідність у XML Infoset
---------------------------------------------------------------------------------
1     ELEMENT_NODE                    Element Information Item
2     ATTRIBUTE_NODE                  Attribute Information Item
3     TEXT_NODE                       Послідовність Character Items
4     CDATA_SECTION_NODE              Секція <![CDATA[...]]> (Character Items)
5     ENTITY_REFERENCE_NODE           Unexpanded Entity Reference
6     ENTITY_NODE                     Entity Declaration
7     PROCESSING_INSTRUCTION_NODE     Processing Instruction Information Item
8     COMMENT_NODE                    Comment Information Item
9     DOCUMENT_NODE                   Document Information Item
10    DOCUMENT_TYPE_NODE              Document Type Declaration Item
11    DOCUMENT_FRAGMENT_NODE          Легковажний контейнер піддерева
12    NOTATION_NODE                   Notation Information Item
```

### Специфікація інтерфейсу `Node` (IDL)

Базовий інтерфейс описує загальні властивості ієрархії, посилання на батьківські та сусідні вузли, а також базові операції мутації графа:

```idl
interface Node {
    // Атрибути ідентифікації та значення
    readonly attribute DOMString       nodeName;
             attribute DOMString       nodeValue;
    readonly attribute unsigned short  nodeType;
    readonly attribute Node            parentNode;
    readonly attribute NodeList        childNodes;
    readonly attribute Node            firstChild;
    readonly attribute Node            lastChild;
    readonly attribute Node            previousSibling;
    readonly attribute Node            nextSibling;
    readonly attribute NamedNodeMap    attributes;
    readonly attribute Document        ownerDocument;

    // Властивості підтримки просторів імен (DOM Level 2/3)
    readonly attribute DOMString       namespaceURI;
             attribute DOMString       prefix;
    readonly attribute DOMString       localName;
             attribute DOMString       textContent;

    // Методи навігації та маніпуляції
    Node               insertBefore(in Node newChild, in Node refChild);
    Node               replaceChild(in Node newChild, in Node oldChild);
    Node               removeChild(in Node oldChild);
    Node               appendChild(in Node newChild);
    boolean            hasChildNodes();
    Node               cloneNode(in boolean deep);
    void               normalize();
    boolean            isSupported(in DOMString feature, in DOMString version);
    boolean            hasAttributes();
};
```

### Специфікація інтерфейсу `Element` (IDL)

Інтерфейс `Element` розширює `Node` специфічними методами пошуку за назвою тегу та доступу до атрибутів з урахуванням просторів імен:

```idl
interface Element : Node {
    readonly attribute DOMString tagName;

    DOMString          getAttribute(in DOMString name);
    void               setAttribute(in DOMString name, in DOMString value);
    void               removeAttribute(in DOMString name);
    Attr               getAttributeNode(in DOMString name);
    NodeList           getElementsByTagName(in DOMString name);

    // Методи з підтримкою просторів імен (Namespace-aware)
    DOMString          getAttributeNS(in DOMString namespaceURI, in DOMString localName);
    void               setAttributeNS(in DOMString namespaceURI, in DOMString qualifiedName, in DOMString value);
    void               removeAttributeNS(in DOMString namespaceURI, in DOMString localName);
    boolean            hasAttribute(in DOMString name);
    boolean            hasAttributeNS(in DOMString namespaceURI, in DOMString localName);
    NodeList           getElementsByTagNameNS(in DOMString namespaceURI, in DOMString localName);
};
```

## 3. SAX 2.0 (Simple API for XML): подієвий push-контракт

Подієвий інтерфейс SAX побудований за патерном «Видавець-Підписник» (Publish-Subscribe) або «Слухач подій» (Event Listener). Синтаксичний аналізатор виконує роль джерела подій: він відкриває потік вводу-виводу, послідовно читає байти і в міру розпізнавання синтаксичних конструкцій викликає методи зворотного виклику (callbacks) зареєстрованого користувацького обробника `ContentHandler`.

### Сигнатури інтерфейсу `org.xml.sax.ContentHandler`

Головний контракт обробки потоку документа, просторів імен, відкривальних та закривальних тегів:

```java
public interface ContentHandler {
    // Керування життєвим циклом документа
    void setDocumentLocator(Locator locator);
    void startDocument() throws SAXException;
    void endDocument() throws SAXException;

    // Зв'язування та розрив префіксів просторів імен
    void startPrefixMapping(String prefix, String uri) throws SAXException;
    void endPrefixMapping(String prefix) throws SAXException;

    // Обробка тегів і тексту
    void startElement(String uri, String localName, String qName, Attributes atts) throws SAXException;
    void endElement(String uri, String localName, String qName) throws SAXException;
    void characters(char[] ch, int start, int length) throws SAXException;
    void ignorableWhitespace(char[] ch, int start, int length) throws SAXException;

    // Додаткові метадані
    void processingInstruction(String target, String data) throws SAXException;
    void skippedEntity(String name) throws SAXException;
}
```

### Сигнатури інтерфейсу `org.xml.sax.Attributes`

Контракт доступу до колекції атрибутів, переданої у виклик `startElement`:

```java
public interface Attributes {
    int getLength();
    String getURI(int index);
    String getLocalName(int index);
    String getQName(int index);
    String getType(int index);       // "CDATA", "ID", "IDREF", "NMTOKEN" тощо
    String getValue(int index);

    int getIndex(String uri, String localName);
    int getIndex(String qName);
    String getType(String uri, String localName);
    String getValue(String uri, String localName);
    String getValue(String qName);
}
```

### Сигнатури інтерфейсу `org.xml.sax.ErrorHandler`

Специфікація обробки діагностичних повідомлень і фатальних збоїв парсера:

```java
public interface ErrorHandler {
    void warning(SAXParseException exception) throws SAXException;
    void error(SAXParseException exception) throws SAXException;
    void fatalError(SAXParseException exception) throws SAXException;
}
```

### Особливості життєвого циклу SAX-обробника

При роботі з SAX важливо враховувати такі правила:
1. **Тимчасовість буфера символів:** масив `char[] ch`, переданий у метод `characters(ch, start, length)`, є внутрішнім робочим буфером парсера. Дані в ньому валідні лише під час виконання поточного методу. Якщо застосунок потребує збереження тексту, він зобов'язаний скопіювати вказаний зріз у власний рядок.
2. **Фрагментація тексту:** один текстовий вузол між тегами може викликати метод `characters()` кілька разів поспіль (наприклад, при переході через межу 8-кілобайтного системного буфера або при обробці сутностей `&amp;`). Обробник зобов'язаний самостійно акумулювати шматки тексту до настання наступної події `startElement` чи `endElement`.
3. **Порядок подій просторів імен:** подія `startPrefixMapping` завжди генерується безпосередньо перед подією `startElement` відповідного вузла, в якому оголошено директиву `xmlns`. Подія `endPrefixMapping` спрацьовує одразу після `endElement`.

## 4. StAX (Streaming API for XML) / `XmlReader`: курсорний pull-контракт

Курсорний потоковий інтерфейс StAX (JSR-173) повертає контроль над потоком виконання клієнтському коду (Pull-модель). Застосунок самостійно викликає метод `next()`, пересуваючи курсор по потоку токенів, та інспектує поточний вузол через гетери `getLocalName()`, `getAttributeValue()` тощо.

### Таблиця числових кодів подій StAX (`XMLStreamConstants`)

Під час виклику методу `next()` курсор повертає цілочисельний код типу поточної синтаксичної одиниці:

| Код події | Назва константи | Опис поточного стану курсора |
| :---: | :--- | :--- |
| `1` | `START_ELEMENT` | Курсор стоїть на відкривальному тегу елемента. Доступні атрибути та простори. |
| `2` | `END_ELEMENT` | Курсор стоїть на закривальному тегу елемента. |
| `3` | `PROCESSING_INSTRUCTION` | Прочитано інструкцію обробки `<?target data?>`. |
| `4` | `CHARACTERS` | Курсор вказує на текстовий блок між тегами. |
| `5` | `COMMENT` | Прочитано коментар `<!-- ... -->`. |
| `6` | `SPACE` | Пробільний текст, що підлягає ігноруванню. |
| `7` | `START_DOCUMENT` | Початок розбору документа (прочитано XML-декларацію). |
| `8` | `END_DOCUMENT` | Кінець потоку документа. |
| `9` | `ENTITY_REFERENCE` | Посилання на іменовану сутність `&name;`. |
| `10` | `ATTRIBUTE` | Окремий атрибут (якщо парсер налаштовано на генерацію подій атрибутів). |
| `11` | `DTD` | Прочитано декларацію типу документа `<!DOCTYPE ...>`. |
| `12` | `CDATA` | Неекранований текстовий блок `<![CDATA[...]]>`. |
| `13` | `NAMESPACE` | Оголошення префікса простору імен `xmlns:prefix="..."`. |

### Специфікація методів курсора `javax.xml.stream.XMLStreamReader`

Повний набір методів для читання, навігації, перевірки передумов та вилучення типізованих значень:

```java
public interface XMLStreamReader extends XMLStreamConstants {
    // Рух курсора
    int     next() throws XMLStreamException;
    void    require(int type, String namespaceURI, String localName) throws XMLStreamException;
    String  getElementText() throws XMLStreamException;
    int     nextTag() throws XMLStreamException;
    boolean hasNext() throws XMLStreamException;
    void    close() throws XMLStreamException;

    // Властивості поточного елемента
    String  getNamespaceURI();
    String  getLocalName();
    String  getPrefix();
    boolean hasName();
    QName   getName();

    // Доступ до атрибутів поточного елемента
    int     getAttributeCount();
    String  getAttributeNamespace(int index);
    String  getAttributeLocalName(int index);
    String  getAttributePrefix(int index);
    String  getAttributeType(int index);
    String  getAttributeValue(int index);
    String  getAttributeValue(String namespaceURI, String localName);
    boolean isAttributeSpecified(int index);

    // Доступ до просторів імен
    int     getNamespaceCount();
    String  getNamespacePrefix(int index);
    String  getNamespaceURI(int index);

    // Доступ до текстового вмісту
    char[]  getTextCharacters();
    int     getTextCharacters(int sourceStart, char[] target, int targetStart, int length) throws XMLStreamException;
    int     getTextStart();
    int     getTextLength();
    String  getText();
    boolean hasText();

    // Діагностика локації у потоці
    Location getLocation();
    int      getEventType();
}
```

### Інженерні переваги pull-моделі

Pull-інтерфейс усуває ключову проблему SAX — необхідність підтримувати складний зовнішній автомат станів (State Machine). Оскільки керування знаходиться в руках застосунку, розробник може:
- Застосовувати **рекурсивний спуск (Recursive Descent Parsing)**: одна функція розбирає тег `<header>`, після чого передає керування функції обробки списку `<items>`, яка в циклі вичитує записи й повертає контроль після досягнення кінцевого тегу.
- Виконувати **вибірковий пропуск піддерев (Subtree Skipping)**: якщо знайдено тег із непотрібними метаданими, метод швидкого пропуску вичитує всі внутрішні токени до відповідного `END_ELEMENT` без створення об'єктів у купі та без виконання бізнес-перевірок.
- Інтегрувати парсер із сучасними механізмами асинхронних генераторів, корутин та каналів (Pipes/Streams).

## 5. Моделі обробки помилок та багатопотокові інваріанти

Важливою частиною інтерфейсного контракту є поведінка парсерів при виникненні помилок та правила роботи в конкурентному середовищі:

1. **Фатальні помилки (Fatal Errors) проти попереджень:**
   Згідно зі специфікацією XML 1.0, будь-яке порушення синтаксису (незакритий тег, невідповідність кодування, подвійне оголошення однакового атрибута) класифікується як фатальна помилка (`fatalError`). Інтерфейсний контракт SAX та StAX вимагає негайного припинення генерації подій і викидання винятку `SAXParseException` або `XMLStreamException`. Метод `error()` викликається лише при порушеннях валідації DTD/XSD (якщо парсер налаштовано в режимі продовження роботи після невідповідності схемі).

2. **Потокобезпечність (Thread Safety):**
   Жоден зі стандартних інтерфейсів (ні `DOMDocument`, ні екземпляри `XMLStreamReader`, ні `ContentHandler`) **не є потокобезпечним (thread-safe)**. Спроба паралельного читання або мутації одного графа DOM із різних потоків без зовнішньої синхронізації призводить до гонитви даних (data race) та пошкодження покажчиків у купі. Спільним патерном для багатопотокових систем є створення окремого екземпляра потокового парсера на кожен робочий потік або побудова незмінного (immutable) графа DOM після завершення розбору.

3. **Контракт звільнення ресурсів:**
   Курсорний інтерфейс `XMLStreamReader` вимагає обов'язкового явного виклику методу `close()` (або використання конструкцій `try-with-resources` / RAII). Оскільки під капотом парсер може утримувати відкриті файлові дескриптори або мережеві сокети, нехтування закриттям курсора призводить до витоку системних дескрипторів операційної системи (file descriptor exhaustion).

## 6. Порівняльна матриця контрактів парсерів

Підсумкове інженерне порівняння чотирьох підходів до синтаксичного розбору та обробки XML:

| Характеристика | W3C DOM | SAX 2.0 | StAX / XmlReader | DOM на базі mmap (PugiXML/RapidXML) |
| :--- | :--- | :--- | :--- | :--- |
| **Модель виконання** | Побудова повного графа в RAM | Push (колбеки парсера) | Pull (ітератор клієнта) | Створення компактного графа без копій |
| **Складність пам'яті** | `O(N)` (5–10× розміру файлу) | `O(1)` (фіксований буфер) | `O(1)` (фіксований буфер) | `O(N)` (1.2–2× розміру файлу) |
| **Керування потоком** | Завантажити все → обробити | Інверсія контролю (парсер) | Прямий цикл (застосунок) | Завантажити все → обробити |
| **Довільний доступ (XPath)** | Повний з коробки | Неможливий | Неможливий | Повний з коробки |
| **Модифікація на льоту** | Дозволена (вставки/видалення) | Лише фільтрація на вихід | Трансформація у вихідний потік | Дозволена |
| **Пропуск піддерев (Skip)** | Немає (все в пам'яті) | Складне ігнорування стану | Простий виклик `skipSubtree()` | Немає (все в пам'яті) |
| **Зручність коду** | Висока (деревоподібний API) | Низька (стеки та стани) | Висока (лінійні цикли) | Дуже висока (C++ ітератори) |
