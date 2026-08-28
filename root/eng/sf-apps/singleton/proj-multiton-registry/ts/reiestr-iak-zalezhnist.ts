// БУЛО: сервіс сам лізе по глобальний логер — прихована залежність, підмінити нема куди
class OrderService {
  process(order: Order) {
    Logger.get("orders").info("нове замовлення");   // ← незримий глобал
  }
}

// СТАЛО: реєстр приходить через конструктор — залежність видно, її можна підмінити
class OrderService {
  constructor(private loggers: LoggerRegistry) {}    // ← видно в сигнатурі

  process(order: Order) {
    this.loggers.get("orders").info("нове замовлення");
  }
}

// збірка програми (один раз, в одному місці):
const loggers = new LoggerRegistry();
const orders = new OrderService(loggers);

// у тесті: підставляємо фейковий реєстр — жодного глобального стану
const fake = new FakeLoggerRegistry();
const sut = new OrderService(fake);
