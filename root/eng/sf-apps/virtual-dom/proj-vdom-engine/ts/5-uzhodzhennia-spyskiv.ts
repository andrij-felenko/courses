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
