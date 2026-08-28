// app.ts (фрагмент) — порт із конфігу + штатне завершення за SIGTERM.
import http from "http";
import { config } from "./config";

const server = http.createServer(app);   // той самий express-застосунок

// Порт — із середовища (крок 1), а не число в коді.
server.listen(config.PORT, "0.0.0.0");

function shutdown(signal: string) {
  // Прийшов SIGTERM: перестаємо брати НОВІ з'єднання,
  // але даємо тим, що вже в роботі, дожити до відповіді.
  server.close(() => {
    // сюди потрапляємо, коли ВСІ активні запити дообслужено:
    //   тепер закрити пул з'єднань до бази, від'єднати Redis — і вийти
    process.exit(0);
  });

  // Страховка: якщо хтось завис і не дає server.close() завершитись,
  // виходимо самі ДО того, як прилетить SIGKILL (вкладаємось у вікно).
  setTimeout(() => process.exit(1), 9000).unref();
}

process.on("SIGTERM", () => shutdown("SIGTERM"));  // ← ввічливе «спинись» від оркестратора
process.on("SIGINT",  () => shutdown("SIGINT"));   // ← Ctrl-C на розробці
