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
