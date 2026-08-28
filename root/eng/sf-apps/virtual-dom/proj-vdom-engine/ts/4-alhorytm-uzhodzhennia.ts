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
