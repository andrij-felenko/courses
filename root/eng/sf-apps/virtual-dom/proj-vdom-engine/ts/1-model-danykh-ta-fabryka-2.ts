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
