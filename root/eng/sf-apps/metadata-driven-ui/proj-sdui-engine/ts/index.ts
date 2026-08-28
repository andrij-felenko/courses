// TypeScript: Безпечний клієнтський рантайм Metadata-Driven UI

export type JsonValue = string | number | boolean | null | JsonObject | JsonArray;
export interface JsonObject { [key: string]: JsonValue; }
export interface JsonArray extends Array<JsonValue> {}

// 1. Граматика безпечних виразів (Safe Expression AST)
export type Expression =
  | boolean
  | number
  | string
  | { var: string }
  | { op: "==" | "!=" | ">" | ">=" | "<" | "<="; left: Expression; right: Expression }
  | { op: "and" | "or"; args: Expression[] }
  | { op: "not"; arg: Expression }
  | { op: "regex"; value: Expression; pattern: string };

// 2. Декларативні вузли інтерфейсу
export interface ValidationRule {
  rule: "required" | "min_length" | "pattern" | "range";
  params?: any;
  message: string;
  when?: Expression;
}

export interface Action {
  type: "SET_STATE" | "NAVIGATE" | "SUBMIT_FORM";
  payload: Record<string, any>;
}

export interface UINode {
  id: string;
  type: string;
  props?: Record<string, any>;
  bind?: { value?: string };
  visibility?: Expression;
  enabled?: Expression;
  validation?: ValidationRule[];
  actions?: Record<string, Action>;
  children?: UINode[];
  fallback?: UINode;
}

// 3. Реактивне сховище стану (State Store)
export class StateStore {
  private state: Record<string, any> = {};
  private listeners = new Set<(path: string, val: any) => void>();

  constructor(initialState: Record<string, any> = {}) {
    this.state = JSON.parse(JSON.stringify(initialState));
  }

  public get(path: string): any {
    if (!path) return undefined;
    const cleanPath = path.startsWith("/") ? path.slice(1) : path;
    const segments = cleanPath.split("/").filter(Boolean);
    let current: any = this.state;
    for (const seg of segments) {
      if (current === null || current === undefined) return undefined;
      current = current[seg];
    }
    return current;
  }

  public set(path: string, value: any): void {
    const cleanPath = path.startsWith("/") ? path.slice(1) : path;
    const segments = cleanPath.split("/").filter(Boolean);
    if (!segments.length) return;

    let current: any = this.state;
    for (let i = 0; i < segments.length - 1; i++) {
      const seg = segments[i];
      if (!(seg in current) || typeof current[seg] !== "object") {
        current[seg] = {};
      }
      current = current[seg];
    }
    current[segments[segments.length - 1]] = value;
    this.listeners.forEach((fn) => fn(path, value));
  }

  public subscribe(fn: (path: string, val: any) => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  public getAll(): Record<string, any> {
    return JSON.parse(JSON.stringify(this.state));
  }
}

// 4. Безпечний обчислювач виразів без eval()
export class SafeExpressionEvaluator {
  public static evaluate(expr: Expression | undefined, store: StateStore): boolean | number | string | null {
    if (expr === undefined || expr === null) return true;
    if (typeof expr === "boolean" || typeof expr === "number" || typeof expr === "string") {
      return expr;
    }

    if ("var" in expr) {
      const val = store.get(expr.var);
      return val !== undefined ? val : null;
    }

    if ("op" in expr) {
      switch (expr.op) {
        case "==":
          return this.evaluate(expr.left, store) === this.evaluate(expr.right, store);
        case "!=":
          return this.evaluate(expr.left, store) !== this.evaluate(expr.right, store);
        case ">":
          return Number(this.evaluate(expr.left, store)) > Number(this.evaluate(expr.right, store));
        case ">=":
          return Number(this.evaluate(expr.left, store)) >= Number(this.evaluate(expr.right, store));
        case "<":
          return Number(this.evaluate(expr.left, store)) < Number(this.evaluate(expr.right, store));
        case "<=":
          return Number(this.evaluate(expr.left, store)) <= Number(this.evaluate(expr.right, store));
        case "and":
          return expr.args.every((arg) => Boolean(this.evaluate(arg, store)));
        case "or":
          return expr.args.some((arg) => Boolean(this.evaluate(arg, store)));
        case "not":
          return !this.evaluate(expr.arg, store);
        case "regex": {
          const target = String(this.evaluate(expr.value, store) ?? "");
          try {
            const re = new RegExp(expr.pattern);
            return re.test(target);
          } catch {
            return false;
          }
        }
      }
    }
    return false;
  }
}

// 5. Рушій валідації (Validation Engine)
export class ValidationEngine {
  public static validateField(val: any, rules: ValidationRule[] | undefined, store: StateStore): string | null {
    if (!rules || !rules.length) return null;

    for (const r of rules) {
      if (r.when && !SafeExpressionEvaluator.evaluate(r.when, store)) {
        continue;
      }
      switch (r.rule) {
        case "required":
          if (val === null || val === undefined || String(val).trim() === "") {
            return r.message;
          }
          break;
        case "min_length":
          if (val && String(val).length < Number(r.params)) {
            return r.message;
          }
          break;
        case "pattern":
          if (val && !new RegExp(r.params).test(String(val))) {
            return r.message;
          }
          break;
        case "range":
          const num = Number(val);
          if (r.params?.min !== undefined && num < r.params.min) return r.message;
          if (r.params?.max !== undefined && num > r.params.max) return r.message;
          break;
      }
    }
    return null;
  }
}

// 6. Реєстр компонентів та диспетчеризація рендерингу
export type ComponentRenderer = (node: UINode, store: StateStore, engine: SDUIEngine) => any;

export class SDUIEngine {
  private registry = new Map<string, ComponentRenderer>();
  public store: StateStore;

  constructor(initialState: Record<string, any> = {}) {
    this.store = new StateStore(initialState);
  }

  public register(type: string, renderer: ComponentRenderer): void {
    this.registry.set(type, renderer);
  }

  public dispatchAction(action: Action): void {
    switch (action.type) {
      case "SET_STATE":
        if (action.payload.path) {
          this.store.set(action.payload.path, action.payload.value);
        }
        break;
      case "SUBMIT_FORM":
        console.log("Відправка форми:", this.store.getAll());
        break;
      case "NAVIGATE":
        console.log("Перехід на екран:", action.payload.screen_id);
        break;
    }
  }

  public renderNode(node: UINode): any {
    // 1. Перевірка видимості
    const isVisible = SafeExpressionEvaluator.evaluate(node.visibility, this.store);
    if (!isVisible) return null;

    // 2. Пошук рендерера в реєстрі
    const renderer = this.registry.get(node.type);
    if (renderer) {
      return renderer(node, this.store, this);
    }

    // 3. Граційна деградація (Fallback)
    if (node.fallback) {
      return this.renderNode(node.fallback);
    }

    // Ігнорування невідомого вузла без падіння процесу
    return null;
  }
}
