interface MediaKeySession extends EventTarget {
  readonly sessionId: string;
  readonly expiration: number;           // Час закінчення ліцензії в епосі Unix (мс) або NaN
  readonly keyStatuses: MediaKeyStatusMap;
  readonly closed: Promise<MediaKeySessionClosedReason>;

  generateRequest(initDataType: string, initData: BufferSource): Promise<void>;
  load(sessionId: string): Promise<boolean>;
  update(response: BufferSource): Promise<void>;
  close(): Promise<void>;
  remove(): Promise<void>;

  onmessage: ((this: MediaKeySession, ev: MediaKeyMessageEvent) => any) | null;
  onkeystatuseschange: ((this: MediaKeySession, ev: Event) => any) | null;
}
