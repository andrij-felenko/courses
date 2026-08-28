interface Element {
  readonly tagName: string;
  readonly attributes: IterableIterator<[string, string]>;
  readonly namespaceURI: string;
  getAttribute(name: string): string | null;
  hasAttribute(name: string): boolean;
  setAttribute(name: string, value: string): this;
  removeAttribute(name: string): this;
  before(content: string, options?: { html?: boolean }): this;
  after(content: string, options?: { html?: boolean }): this;
  prepend(content: string, options?: { html?: boolean }): this;
  append(content: string, options?: { html?: boolean }): this;
  setInnerContent(content: string, options?: { html?: boolean }): this;
  remove(): this;
  removeAndKeepContent(): this;
}

interface HTMLRewriter {
  on(selector: string, handlers: {
    element?(element: Element): void | Promise<void>;
    comments?(comment: unknown): void | Promise<void>;
    text?(text: unknown): void | Promise<void>;
  }): this;
  transform(response: Response): Response;
}
