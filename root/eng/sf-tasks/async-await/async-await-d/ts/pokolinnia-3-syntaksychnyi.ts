// Сучасний вигляд: лінійний потік, нативний try/catch, прозорі змінні
async function handleUserRequest(userId: string): Promise<Response> {
  try {
    const config = await loadConfig();
    const db = await connectDatabase(config.dbUrl);
    const user = await authenticateUser(db, token);
    const account = await fetchAccount(db, user.id);
    
    return { status: 200, body: { user, account } };
  } catch (err) {
    logger.error("Помилка обробки запиту:", err);
    return { status: 500, body: { error: "Внутрішній збій" } };
  }
}
