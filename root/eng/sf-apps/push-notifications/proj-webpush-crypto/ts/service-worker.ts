// service-worker.ts — клієнтський обробник у браузері
self.addEventListener('push', (event: PushEvent) => {
  if (!event.data) {
    console.warn('Отримано тихий пуш без корисного навантаження');
    return;
  }

  // Отримання розшифрованого JSON-об'єкта
  const payload = event.data.json();

  const title = payload.title || 'Нове сповіщення';
  const options: NotificationOptions = {
    body: payload.body,
    icon: payload.icon || '/icons/notification-192.png',
    badge: '/icons/badge-72.png',
    data: {
      url: payload.url || '/'
    }
  };

  // Показ системного сповіщення через Notification API
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});
