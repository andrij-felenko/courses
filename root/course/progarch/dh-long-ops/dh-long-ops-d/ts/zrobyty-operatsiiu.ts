// «Квитанція» замість очікування: операція — це РЕСУРС зі своїм життям.
type OpStatus = "queued" | "running" | "succeeded" | "failed" | "canceled";

interface ClipOperation {
  id: string;                 // /operations/{id} — за цим клієнт стежить
  status: OpStatus;
  progress: number;           // 0..100, поки running
  request: { cameraId: string; from: string; to: string };  // що саме просили
  result?: { url: string; expiresAt: string };  // з'явиться, коли succeeded
  error?: { code: string; message: string };     // з'явиться, коли failed
  createdAt: string;
}
