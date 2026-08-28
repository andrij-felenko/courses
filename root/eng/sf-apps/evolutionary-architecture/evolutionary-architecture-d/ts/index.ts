// Зчеплення ПОЗИЦІЄЮ: зміст аргументів тримається на порядку.
function schedule(userId: string, retries: number, timeoutMs: number) { /* ... */ }
schedule("u-42", 3, 5000);
// Переставив 3 і 5000 місцями — типи збіглися, компілятор мовчить,
// а логіка вже бреше: 5000 спроб і таймаут 3 мс. Зламалось тихо.

// Зчеплення ІМЕНЕМ: порядок більше не несе змісту.
function schedule2(o: { userId: string; retries: number; timeoutMs: number }) { /* ... */ }
schedule2({ userId: "u-42", timeoutMs: 5000, retries: 3 });
// Порядок довільний — сенс тримає ім'я поля, переставити безпечно.
