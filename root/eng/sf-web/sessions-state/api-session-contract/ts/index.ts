export interface ISessionStore {
  create(initialData?: SessionData, ttlSeconds?: number): Promise<SessionEnvelope>;
  get(sessionId: string): Promise<SessionEnvelope | null>;
  update(
    sessionId: string,
    expectedVersion: number,
    mutator: (current: SessionData) => SessionData,
    ttlSeconds?: number
  ): Promise<SessionEnvelope>;
  touch(sessionId: string, ttlSeconds?: number): Promise<boolean>;
  destroy(sessionId: string): Promise<boolean>;
  destroyAllForUser(userId: string): Promise<number>;
  rotate(oldSessionId: string, ttlSeconds?: number): Promise<SessionEnvelope>;
}
