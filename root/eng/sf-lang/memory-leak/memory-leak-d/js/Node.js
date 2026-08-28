// JavaScript / Node.js
class UserSessionManager {
    constructor() {
        // Глобальна мапа живе весь час роботи сервера (GC Root)
        this.activeSessions = new Map();
    }

    login(userId, sessionPayload) {
        // Кожна авторизація додає новий великий об'єкт
        this.activeSessions.set(userId, {
            data: sessionPayload,
            createdAt: Date.now()
        });
    }

    // Якщо розробник забув викликати logout або таймер очищення,
    // сесії накопичуватимуться, доки процес не вичерпає ліміт пам'яті V8
}
