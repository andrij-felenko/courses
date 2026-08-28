import { test, expect } from "@playwright/test";

test("успішна безпарольна реєстрація та вхід через віртуальний Passkey", async ({ page }) => {
  // Створюємо сесію CDP до браузера
  const client = await page.context().newCDPSession(page);

  // Вмикаємо емуляцію середовища WebAuthn
  await client.send("WebAuthn.enable");

  // Додаємо віртуальний біометричний автентифікатор із підтримкою Passkeys
  const { authenticatorId } = await client.send("WebAuthn.addVirtualAuthenticator", {
    options: {
      protocol: "ctap2",
      transport: "internal",
      hasResidentKey: true,
      hasUserVerification: true,
      isUserVerified: true,
      automaticPresenceSimulation: true,
    },
  });

  // Відкриваємо сторінку реєстрації
  await page.goto("https://example.com/register");
  await page.fill("#email", "alice@example.com");
  await page.click("#btn-register-passkey");

  // Перевіряємо успішне створення запису в UI
  await expect(page.locator("#status-message")).toHaveText("Ключ успішно зареєстровано!");

  // Тестуємо вхід в один клік
  await page.goto("https://example.com/login");
  await page.click("#btn-login-passkey");

  // Перевіряємо авторизований стан
  await expect(page.locator("#user-profile")).toBeVisible();

  // Прибираємо віртуальний автентифікатор
  await client.send("WebAuthn.removeVirtualAuthenticator", { authenticatorId });
});
