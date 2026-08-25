# ⚙️ Мінімальний VDOM-рушій: h, diff та patch

Реалізація власного рушія Virtual DOM дозволяє розібрати механізм декларативного рендерингу на найпростіші складники. Нижче наведено повнофункціональний, типізований рушій мовою TypeScript, який реалізує повний життєвий цикл роботи з віртуальними деревами: конструювання вузлів, їхнє первинне монтування в браузерний DOM, покрокове узгодження властивостей і списків дітей із підтримкою ключів, а також чергу пакетування оновлень.

## 1. Модель даних та фабрика віртуальних вузлів

Віртуальний вузол (VNode) — це проста структура даних у пам'яті JavaScript. Вона не містить методів чи прихованого стану, що робить її надзвичайно дешевою для створення, клонування та серіалізації.

```ts
export type VNodeChild = VNode | string | number | null | undefined | boolean;

export interface VNodeProps {
  key?: string | number;
  className?: string;
  style?: Record<string, string>;
  onClick?: (e: MouseEvent) => void;
  [key: string]: any;
}

export interface VNode {
  tag: string;
  props: VNodeProps;
  children: VNodeChild[];
  key?: string | number;
  dom?: Node; // Пряме посилання на відповідний створений DOM-вузол
}
```

Фабрична функція `h` (скорочення від *hyperscript* — вираз для створення гіпертексту) приймає назву тегу, об'єкт властивостей та довільну кількість дочірніх елементів. Вона автоматично розгортає вкладені масиви та відфільтровує булеві значення й порожні елементи (`null`, `undefined`), що суттєво спрощує використання умовного рендерингу у виразах на кшталт `{isOpen && h('div', null, 'Контент')}`.

```ts
/**
 * Фабрика віртуальних вузлів
 */
export function h(
  tag: string,
  props: VNodeProps | null,
  ...children: (VNodeChild | VNodeChild[])[]
): VNode {
  const flatChildren = children
    .flat(Infinity)
    .filter(
      (c): c is VNode | string | number =>
        c !== null && c !== undefined && c !== false && c !== true
    );

  return {
    tag,
    props: props || {},
    children: flatChildren,
    key: props?.key,
  };
}
```

## 2. Первинне монтування віртуального вузла в DOM

Функція `createElement` відповідає за перетворення віртуального вузла на фізичний вузол браузера (`HTMLElement` або `Text`).

Процес монтування складається з чотирьох послідовних кроків:
1. **Обробка примітивів:** якщо передано рядок або число, створюється нативний текстовий вузол через `document.createTextNode()`.
2. **Створення елемента:** для об'єктних VNode викликається `document.createElement(vnode.tag)`.
3. **Збереження зворотного посилання:** посилання на створений DOM-елемент записується в поле `vnode.dom`. Це посилання є критично важливим, оскільки саме воно дозволяє наступним фазам дифінгу оновлювати вузол на місці без повторного пошуку через селектори `querySelector`.
4. **Рекурсивне монтування дітей:** кожен дочірній елемент монтується та вставляється у батьківський вузол за допомогою `appendChild()`.

```ts
/**
 * Створення реального DOM-вузла на основі VNode
 */
export function createElement(vnode: VNodeChild): Node {
  // 1. Обробка текстових вузлів
  if (typeof vnode === "string" || typeof vnode === "number") {
    return document.createTextNode(String(vnode));
  }

  if (!vnode) {
    return document.createTextNode("");
  }

  // 2. Створення HTML-елемента
  const el = document.createElement(vnode.tag);
  vnode.dom = el;

  // 3. Застосування початкових властивостей
  patchProps(el, {}, vnode.props);

  // 4. Рекурсивне монтування дітей
  for (const child of vnode.children) {
    const childDom = createElement(child);
    el.appendChild(childDom);
  }

  return el;
}
```

## 3. Синхронізація властивостей та обробників подій

Функція `patchProps` ізолює логіку оновлення атрибутів, класів, інлайн-стилів та слухачів подій. Вона виконує дві послідовні фази: повне видалення застарілих властивостей і встановлення або оновлення нових.

Особливу увагу приділено обробникам подій: якщо функція-слухач змінилася, старий обробник обов'язково відв'язується через `removeEventListener`, щоб уникнути витоків пам'яті та повторного виконання застарілих замикань на старий стан.

```ts
/**
 * Синхронізація властивостей між старим і новим набором
 */
export function patchProps(
  el: HTMLElement,
  oldProps: VNodeProps,
  newProps: VNodeProps
): void {
  // Фаза 1: Видалення властивостей, яких більше немає
  for (const key of Object.keys(oldProps)) {
    if (key === "key") continue;
    if (!(key in newProps)) {
      if (key.startsWith("on")) {
        const eventName = key.slice(2).toLowerCase();
        el.removeEventListener(eventName, oldProps[key]);
      } else if (key === "className") {
        el.removeAttribute("class");
      } else if (key === "style") {
        el.removeAttribute("style");
      } else {
        el.removeAttribute(key);
      }
    }
  }

  // Фаза 2: Додавання та оновлення нових властивостей
  for (const [key, value] of Object.entries(newProps)) {
    if (key === "key") continue;
    const oldValue = oldProps[key];
    if (oldValue === value) continue;

    if (key.startsWith("on")) {
      const eventName = key.slice(2).toLowerCase();
      if (oldValue) el.removeEventListener(eventName, oldValue);
      if (value) el.addEventListener(eventName, value);
    } else if (key === "className") {
      el.className = value || "";
    } else if (key === "style" && typeof value === "object") {
      // Очищення видалених CSS-властивостей всередині об'єкта style
      if (typeof oldValue === "object" && oldValue !== null) {
        for (const styleKey of Object.keys(oldValue)) {
          if (!(styleKey in value)) {
            (el.style as any)[styleKey] = "";
          }
        }
      }
      Object.assign(el.style, value);
    } else if (typeof value === "boolean") {
      // Обробка булевих атрибутів (disabled, checked тощо)
      if (value) {
        el.setAttribute(key, "");
        (el as any)[key] = true;
      } else {
        el.removeAttribute(key);
        (el as any)[key] = false;
      }
    } else {
      el.setAttribute(key, String(value));
    }
  }
}
```

## 4. Алгоритм узгодження (Diffing & Patching)

Головна функція `patch` порівнює два віртуальні вузли й мутує реальний DOM із мінімальною кількістю системних операцій.

Логіка прийняття рішень складається з п'яти взаємовиключних гілок:
1. **Монтування:** якщо старого вузла не існувало (`oldVNode === undefined`), новий вузол створюється та додається до батьківського контейнера через `appendChild()`.
2. **Демонтаж:** якщо новий вузол став порожнім (`newVNode === undefined`), відповідний старий DOM-елемент видаляється з документа через `removeChild()`.
3. **Текстове узгодження:** якщо обидва вузли є текстом, але їхній зміст різниться, оновлюється лише поле `nodeValue` нативного текстового вузла. Сам DOM-елемент не перестворюється.
4. **Заміна піддерева (Евристика різних тегів):** якщо старий і новий вузли мають різні теги (наприклад, `<div>` замінено на `<section>`), алгоритм не спускається вглиб. Він створює новий DOM-вузол і підміняє старе піддерево через `parent.replaceChild(newDom, oldDom)`.
5. **Точкове оновлення (Однакові теги):** посилання на реальний DOM-елемент копіюється зі старого VNode у новий (`newVNode.dom = oldVNode.dom`), після чого виконується дифінг властивостей (`patchProps`) та рекурсивне узгодження дітей (`patchChildren`).

```ts
/**
 * Головна функція узгодження двох вузлів
 */
export function patch(
  parent: Node,
  newVNode: VNodeChild,
  oldVNode?: VNodeChild,
  index: number = 0
): Node | undefined {
  // 1. Монтування нового елемента
  if (oldVNode === undefined || oldVNode === null) {
    const newDom = createElement(newVNode);
    parent.appendChild(newDom);
    return newDom;
  }

  // 2. Демонтаж старого елемента
  if (newVNode === undefined || newVNode === null) {
    const oldDom = getDomNode(oldVNode, parent, index);
    if (oldDom && oldDom.parentNode === parent) {
      parent.removeChild(oldDom);
    }
    return undefined;
  }

  // 3. Порівняння текстових вузлів
  if (
    (typeof oldVNode === "string" || typeof oldVNode === "number") &&
    (typeof newVNode === "string" || typeof newVNode === "number")
  ) {
    const oldDom = getDomNode(oldVNode, parent, index);
    if (oldVNode !== newVNode && oldDom) {
      oldDom.nodeValue = String(newVNode);
    }
    return oldDom;
  }

  // 4. Заміна піддерева при зміні типу або тегу
  if (
    typeof oldVNode !== typeof newVNode ||
    (typeof oldVNode === "object" &&
      typeof newVNode === "object" &&
      oldVNode.tag !== newVNode.tag)
  ) {
    const oldDom = getDomNode(oldVNode, parent, index);
    const newDom = createElement(newVNode);
    if (oldDom && oldDom.parentNode === parent) {
      parent.replaceChild(newDom, oldDom);
    }
    return newDom;
  }

  // 5. Оновлення існуючого елемента однакового типу
  const oldVNodeObj = oldVNode as VNode;
  const newVNodeObj = newVNode as VNode;
  const dom = (newVNodeObj.dom = oldVNodeObj.dom as HTMLElement);

  // Оновлення властивостей
  patchProps(dom, oldVNodeObj.props, newVNodeObj.props);

  // Рекурсивне узгодження списку дітей
  patchChildren(dom, oldVNodeObj.children, newVNodeObj.children);

  return dom;
}

function getDomNode(vnode: VNodeChild, parent: Node, index: number): Node | undefined {
  if (typeof vnode === "object" && vnode !== null && vnode.dom) {
    return vnode.dom;
  }
  return parent.childNodes[index];
}
```

## 5. Узгодження списків дітей із підтримкою ключів

Функція `patchChildren` реалізує стратегію зіставлення елементів за ключами за допомогою хеш-карти.

Механізм роботи з ключами складається з таких кроків:
1. **Індексація старих дітей:** формується таблиця `oldKeyMap = Map<key, { vnode, index }>`.
2. **Прохід по новому списку:** для кожного нового елемента шукається відповідник у карті.
   - Якщо ключ знайдено: викликається `patch` для оновлення атрибутів, а вузол видаляється з карти.
   - Якщо індекс старого вузла менший за максимальний уже пройдений індекс (`matched.index < lastPlacedIndex`), це означає, що елемент перемістився відносно сусідів, і викликається `parent.insertBefore()`.
   - Якщо ключа немає у старій карті: це новий елемент, який монтується через `createElement()` та вставляється у потрібну позицію.
3. **Очищення залишку:** усі вузли, що залишилися в `oldKeyMap` після завершення проходу, видаляються з реального DOM як більше не потрібні.

```ts
/**
 * Звіряння двох списків дітей
 */
function patchChildren(
  parent: HTMLElement,
  oldChildren: VNodeChild[],
  newChildren: VNodeChild[]
): void {
  const hasKeys = newChildren.some(
    (c) => typeof c === "object" && c !== null && c.key !== undefined
  );

  // Простий поіндексний алгоритм для неключованих списків
  if (!hasKeys) {
    const commonLength = Math.min(oldChildren.length, newChildren.length);
    for (let i = 0; i < commonLength; i++) {
      patch(parent, newChildren[i], oldChildren[i], i);
    }
    if (newChildren.length > oldChildren.length) {
      for (let i = commonLength; i < newChildren.length; i++) {
        parent.appendChild(createElement(newChildren[i]));
      }
    } else if (oldChildren.length > newChildren.length) {
      for (let i = oldChildren.length - 1; i >= commonLength; i--) {
        const oldDom = getDomNode(oldChildren[i], parent, i);
        if (oldDom && oldDom.parentNode === parent) {
          parent.removeChild(oldDom);
        }
      }
    }
    return;
  }

  // Ключоване узгодження через хеш-таблицю
  const oldKeyMap = new Map<string | number, { vnode: VNode; index: number }>();
  oldChildren.forEach((child, index) => {
    if (typeof child === "object" && child !== null && child.key !== undefined) {
      oldKeyMap.set(child.key, { vnode: child, index });
    }
  });

  let lastPlacedIndex = 0;

  for (let i = 0; i < newChildren.length; i++) {
    const newChild = newChildren[i];
    if (typeof newChild !== "object" || newChild === null || newChild.key === undefined) {
      continue;
    }

    const matched = oldKeyMap.get(newChild.key);

    if (matched) {
      // Збіг за ключем — оновлюємо вузол
      patch(parent, newChild, matched.vnode, matched.index);
      oldKeyMap.delete(newChild.key);

      // Визначаємо, чи потрібно перемістити DOM-вузол
      if (matched.index < lastPlacedIndex) {
        const nextSibling = parent.childNodes[i] || null;
        parent.insertBefore(newChild.dom!, nextSibling);
      } else {
        lastPlacedIndex = matched.index;
      }
    } else {
      // Новий елемент — створюємо і вставляємо на поточну позицію
      const newDom = createElement(newChild);
      const nextSibling = parent.childNodes[i] || null;
      parent.insertBefore(newDom, nextSibling);
    }
  }

  // Видалення старих вузлів, які не увійшли до нового списку
  for (const { vnode } of oldKeyMap.values()) {
    if (vnode.dom && vnode.dom.parentNode === parent) {
      parent.removeChild(vnode.dom);
    }
  }
}
```

## 6. Пакетування оновлень через мікрозадачі (Batching Queue)

Щоб синхронні мутації стану не викликали багаторазового повторного рендерингу та зайвих циклів дифінгу, рушій об'єднує всі запити у чергу мікрозадач за допомогою нативної функції `queueMicrotask()`.

Якщо компонент викликає зміну кількох полів стану підряд в одному обробнику події, рендеринг відбудеться рівно один раз у кінці поточного макротаска браузера.

```ts
type RenderCallback = () => void;

class RenderScheduler {
  private queue = new Set<RenderCallback>();
  private isScheduled = false;

  schedule(callback: RenderCallback): void {
    this.queue.add(callback);

    if (!this.isScheduled) {
      this.isScheduled = true;
      queueMicrotask(() => this.flush());
    }
  }

  private flush(): void {
    for (const callback of this.queue) {
      callback();
    }
    this.queue.clear();
    this.isScheduled = false;
  }
}

export const scheduler = new RenderScheduler();
```

## 7. Покрокове простеження узгодження (Tracing Walkthrough)

Розглянемо детальний стан змінних та викликів DOM API на конкретному прикладі трансформації списку елементів.

Нехай у батьківському контейнері вже змонтовано список із трьох елементів:
- **Старий стан:** `[ Item A (key: 1), Item B (key: 2), Item C (key: 3) ]`
- **Новий стан:** `[ Item C (key: 3), Item A (key: 1), Item D (key: 4) ]`

### Покроковий протокол виконання `patchChildren`:

1. **Фаза індексації:** створюється `oldKeyMap`:
   - `key: 1 → { vnode: Item A, index: 0 }`
   - `key: 2 → { vnode: Item B, index: 1 }`
   - `key: 3 → { vnode: Item C, index: 2 }`
   - `lastPlacedIndex = 0`

2. **Ітерація `i = 0` (Обробка `Item C`, key: 3):**
   - Ключ `3` знайдено в `oldKeyMap` на старій позиції `index = 2`.
   - Викликається `patch(parent, newC, oldC)` для синхронізації властивостей.
   - Видаляємо ключ `3` з карти.
   - Перевірка переміщення: `matched.index (2) >= lastPlacedIndex (0)` → елемент не переміщується в DOM!
   - Оновлюємо `lastPlacedIndex = 2`.
   - `Item C` залишається на своїй фізичній позиції в DOM як якір.

3. **Ітерація `i = 1` (Обробка `Item A`, key: 1):**
   - Ключ `1` знайдено в `oldKeyMap` на старій позиції `index = 0`.
   - Викликається `patch(parent, newA, oldA)`.
   - Видаляємо ключ `1` з карти.
   - Перевірка переміщення: `matched.index (0) < lastPlacedIndex (2)` → **умова істинна!** Вузол `Item A` опинився позаду якоря.
   - Викликається `parent.insertBefore(domA, parent.childNodes[1])` — вузол фізично переноситься на другу позицію в DOM.
   - `lastPlacedIndex` залишається рівним `2`.

4. **Ітерація `i = 2` (Обробка `Item D`, key: 4):**
   - Ключа `4` немає в `oldKeyMap` → це абсолютно новий елемент!
   - Викликається `createElement(newD)` для створення нового `HTMLElement`.
   - Викликається `parent.insertBefore(domD, parent.childNodes[2])` — новий вузол додається на третю позицію в DOM.

5. **Фаза очищення (Залишок у карті):**
   - У `oldKeyMap` залишився запис для `key: 2` (`Item B`).
   - Викликається `parent.removeChild(domB)` — вузол `Item B` видаляється з документа.

У результаті алгоритм виконав рівно одне переміщення `insertBefore` для `Item A`, одну вставку для `Item D` та одне видалення для `Item B`. Вузол `Item C` залишився нерухомим.

## 8. Пастки та крайові випадки при розробці VDOM-рушіїв

Під час практичної розробки рушіїв рендерингу виникає низка специфічних крайових ситуацій:

1. **Змішані списки (з ключами та без):** якщо розробник задає `key` лише для частини братніх вузлів, неключовані елементи ризикують бути проігнорованими або помилково видаленими під час очищення `oldKeyMap`. Промислові рушії вимагають або повної наявності ключів у всіх дітей колекції, або генерують попередження в консолі розробника.
2. **Дублікати ключів (Duplicate Keys):** якщо два елементи мають однаковий `key`, другий елемент перезапише посилання в `oldKeyMap`. Під час фази видалення рушій спробує двічі видалити один і той самий DOM-вузол, що призведе до аварійного винятку `NotFoundError: Failed to execute 'removeChild' on 'Node'`.
3. **Керовані поля форми (`<input value="...">`):** пряме встановлення атрибута `el.setAttribute('value', val)` не змінює поточний текст у полі, якщо користувач уже ввів туди символи з клавіатури. Рушій зобов'язаний мутувати безпосередню властивість об'єкта `(el as HTMLInputElement).value = val`.
4. **Витоки пам'яті через замикання в обробниках:** якщо при видаленні піддерева не зняти слухачі подій або не розірвати посилання `vnode.dom = undefined`, збирач сміття V8 не зможе звільнити пам'ять вилучених DOM-вузлів через циклічні посилання між замиканнями та C++ об'єктами ядра.

## 9. Практичний приклад: інтерактивний список із сортуванням

Нижче наведено робочий приклад інтеграції створеного рушія з реактивним компонентом списку завдань:

```ts
interface TodoItem {
  id: number;
  title: string;
  completed: boolean;
}

class TodoApp {
  private state: { todos: TodoItem[]; count: number } = {
    todos: [
      { id: 1, title: "Написати VDOM рушій", completed: true },
      { id: 2, title: "Реалізувати алгоритм узгодження", completed: true },
      { id: 3, title: "Оптимізувати роботу зі списками через key", completed: false },
    ],
    count: 0,
  };

  private vnode: VNode | null = null;
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;
    this.render();
  }

  setState(updater: (prev: typeof this.state) => void): void {
    updater(this.state);
    scheduler.schedule(() => this.render());
  }

  private render(): void {
    const newVNode = h(
      "div",
      { className: "todo-app" },
      h("h1", null, "Список завдань (Оновлень: ", this.state.count, ")"),
      h(
        "div",
        { className: "toolbar", style: { marginBottom: "15px" } },
        h(
          "button",
          {
            onClick: () => {
              this.setState((s) => {
                s.count++;
                s.todos.reverse(); // Реверс порядку для перевірки key-переміщень
              });
            },
          },
          "Розвернути список"
        ),
        h(
          "button",
          {
            onClick: () => {
              this.setState((s) => {
                s.count++;
                s.todos.unshift({
                  id: Date.now(),
                  title: `Нове завдання #${s.todos.length + 1}`,
                  completed: false,
                });
              });
            },
          },
          "Додати на початок"
        )
      ),
      h(
        "ul",
        { className: "todo-list" },
        this.state.todos.map((todo) =>
          h(
            "li",
            {
              key: todo.id,
              className: todo.completed ? "completed" : "",
              style: { padding: "6px 0" },
            },
            h("input", {
              type: "checkbox",
              checked: todo.completed,
              onClick: () => {
                this.setState((s) => {
                  s.count++;
                  const item = s.todos.find((t) => t.id === todo.id);
                  if (item) item.completed = !item.completed;
                });
              },
            }),
            h("span", { style: { marginLeft: "8px" } }, todo.title)
          )
        )
      )
    );

    patch(this.container, newVNode, this.vnode);
    this.vnode = newVNode;
  }
}

// Запуск застосунку
const root = document.getElementById("app")!;
new TodoApp(root);
```

Завдяки збереженню посилання `vnode.dom` та зіставленню за `todo.id`, натискання кнопки «Розвернути список» не викликає повторного створення DOM-вузлів `<li>`: рушій виконує рівно необхідну кількість викликів `insertBefore` для перестановки елементів у новому порядку, зберігаючи внутрішній стан прапорців та активний фокус користувача.
