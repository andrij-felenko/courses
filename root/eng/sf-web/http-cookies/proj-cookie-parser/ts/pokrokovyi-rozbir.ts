import { parseCookies, serializeSetCookie, verifySignedCookie } from "./cookie_engine";

// Тест 1: Розбір складних значень (Base64 із символами '=', лапки, зайві пробіли)
const complexHeader = '  sid="dGhpcz1zZWNyZXQ=="; theme=dark; empty_val=; unquoted=a=b=c; ';
const parsed = parseCookies(complexHeader);

console.assert(parsed.get("sid") === "dGhpcz1zZWNyZXQ==", "Помилка парсингу Base64 у подвійних лапках");
console.assert(parsed.get("theme") === "dark", "Помилка парсингу theme");
console.assert(parsed.get("empty_val") === "", "Помилка парсингу порожнього значення");
console.assert(parsed.get("unquoted") === "a=b=c", "Помилка збереження знаків '=' усередині значення");

// Тест 2: Захист від помилкової конфігурації префікса __Host-
try {
  serializeSetCookie("__Host-auth", "tok123", {
    domain: "example.com", // Неприпустимо для __Host-
    secure: true,
    path: "/"
  });
  console.assert(false, "Помилка: валідатор пропустив domain для __Host- cookie!");
} catch (err: any) {
  console.assert(err.message.includes("забороняє вказувати domain"), "Очікувана помилка валідації Domain");
}

// Тест 3: Генерація суворого захищеного заголовка для сесії
const validSetCookie = serializeSetCookie("__Host-session", "random_token_99", {
  secure: true,
  httpOnly: true,
  path: "/",
  sameSite: "Lax",
  maxAge: 3600
});

console.log("Згенеровано валідний заголовок Set-Cookie:");
console.log(validSetCookie);

// Тест 4: Перевірка валідації підписаних токенів у константному часі
const secret = "super-secret-key-12345";
const validToken = "usr_42.tX9s7Y_abc_signature"; // припустимий підпис
// Якщо підпис недійсний, функція повертає null
console.assert(verifySignedCookie("usr_42.invalid_sig", secret) === null, "Помилка: пропущено підроблений підпис!");
