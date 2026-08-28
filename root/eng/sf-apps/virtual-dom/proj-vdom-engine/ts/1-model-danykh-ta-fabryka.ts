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
