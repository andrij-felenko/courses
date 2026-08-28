// Перевірка та запит доступу до сторонніх cookie всередині iframe
if (document.requestStorageAccess) {
  document.hasStorageAccess().then(hasAccess => {
    if (!hasAccess) {
      // Вимагає прямої взаємодії користувача (User Gesture: клік або тач)
      document.requestStorageAccess().then(
        () => { /* Доступ надано: document.cookie тепер бачить власні cookie */ },
        () => { /* Користувач або браузер відхилив доступ */ }
      );
    }
  });
}
