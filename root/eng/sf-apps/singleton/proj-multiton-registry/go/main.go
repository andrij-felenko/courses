// Go: подвійна перевірка на RWMutex. Спершу дешеве читання під RLock;
// якщо промах — беремо ексклюзивний Lock і перевіряємо ще раз, уже під ним.
type LoggerRegistry struct {
    mu      sync.RWMutex
    loggers map[string]*Logger
}

func NewLoggerRegistry() *LoggerRegistry {
    return &LoggerRegistry{loggers: make(map[string]*Logger)}
}

func (r *LoggerRegistry) Get(name string) *Logger {
    r.mu.RLock()
    lg, ok := r.loggers[name]
    r.mu.RUnlock()
    if ok {
        return lg // швидкий шлях: ключ уже є, жодного ексклюзивного замка
    }

    r.mu.Lock()
    defer r.mu.Unlock()
    if lg, ok := r.loggers[name]; ok { // друга перевірка: хтось міг створити, поки ми брали Lock
        return lg
    }
    lg = newLogger(name)
    r.loggers[name] = lg
    return lg
}
