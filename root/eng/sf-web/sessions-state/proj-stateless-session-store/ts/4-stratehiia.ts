export async function mutateSessionWithRetry(
  store: StatelessRedisSessionStore,
  sessionId: string,
  mutator: (data: SessionData) => SessionData,
  maxRetries = 3
): Promise<SessionEnvelope> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const session = await store.get(sessionId);
    if (!session) {
      throw new Error(`Cannot mutate non-existent session ${sessionId}`);
    }

    try {
      return await store.update(sessionId, session.version, mutator);
    } catch (err: unknown) {
      if ((err as Error).name === "VersionConflictError" && attempt < maxRetries) {
        // Експоненційне затримання з випадковим джитером для запобігання повторним колізіям
        const backoffMs = Math.random() * 15 * attempt;
        await new Promise((resolve) => setTimeout(resolve, backoffMs));
        continue;
      }
      throw err;
    }
  }

  throw new Error(`CONCURRENCY_ERROR: exceeded max retries for session ${sessionId}`);
}
