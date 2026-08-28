class SessionService {
  private hits = 0;
  private sessions = new Map<string, Session>();

  // ЗАПИТ: лише повертає, стан не чіпає. Клич скільки хоч.
  getSession(id: string): Session | undefined {
    return this.sessions.get(id);
  }

  // КОМАНДА: явно реєструє перегляд. Нічого не повертає.
  recordSessionView(id: string): void {
    this.hits += 1;
  }

  // ЗАПИТ на саму метрику — теж чистий.
  viewCount(): number {
    return this.hits;
  }
}
