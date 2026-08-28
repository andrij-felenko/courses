interface XMLHttpRequest extends XMLHttpRequestEventTarget {
  open(method: string, url: string, async?: boolean, user?: string, password?: string): void;
  setRequestHeader(name: string, value: string): void;
  send(body?: Document | XMLHttpRequestBodyInit | null): void;
  abort(): void;

  readonly readyState: number;
  readonly status: number;
  readonly statusText: string;
  readonly responseText: string;
  readonly responseXML: Document | null;
  responseType: XMLHttpRequestResponseType; // "" | "arraybuffer" | "blob" | "document" | "json" | "text"

  readonly upload: XMLHttpRequestUpload; // Надає події progress, load, error для тіла POST-запиту

  onreadystatechange: ((this: XMLHttpRequest, ev: Event) => any) | null;
  onload: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
  onerror: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
  onprogress: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
  ontimeout: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
}
