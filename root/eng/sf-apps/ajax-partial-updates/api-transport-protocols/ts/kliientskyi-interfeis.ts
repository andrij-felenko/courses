const sse = new EventSource("/api/live-feed", { withCredentials: true });

// Обробка стандартних подій без зазначеного типу
sse.onmessage = (event: MessageEvent) => {
  const payload = JSON.parse(event.data);
  console.log("Отримано базове повідомлення:", payload);
};

// Підписка на кастомний тип події (поле event: user_alert)
sse.addEventListener("user_alert", (event: MessageEvent) => {
  displayAlertBanner(event.data);
});

// Обробка стану з'єднання та помилок
sse.onerror = (err) => {
  if (sse.readyState === EventSource.CLOSED) {
    console.error("З'єднання остаточно закрито сервером");
  } else if (sse.readyState === EventSource.CONNECTING) {
    console.warn("Тимчасовий обрив; браузер виконує автоматичний reconnect");
  }
};
