function fetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response>;

interface RequestInit {
  method?: string;
  headers?: HeadersInit;
  body?: BodyInit | null;
  mode?: "cors" | "no-cors" | "same-origin" | "navigate";
  credentials?: "omit" | "same-origin" | "include";
  cache?: "default" | "no-store" | "reload" | "no-cache" | "force-cache" | "only-if-cached";
  redirect?: "follow" | "error" | "manual";
  signal?: AbortSignal | null;
  keepalive?: boolean;
}
