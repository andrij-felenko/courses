type UserId = string & { readonly __brand: "UserId" };

// Порт: одне слово нашою мовою — щоб ядро не знало ні пошти, ні пушів, ні SMS.
interface Notifier {
  notify(userId: UserId, text: string): Promise<void>;
}

// Готові речі, яких ми не писали: бібліотека розсилання й довідник людей.
interface Mailer        { send(msg: { to: string; subject: string; body: string }): Promise<void>; }
interface UserDirectory { emailOf(userId: UserId): Promise<string>; }

// Адаптер: уся «логіка» — перекласти НАШ виклик у виклик бібліотеки.
class EmailNotifier implements Notifier {
  constructor(private mailer: Mailer, private users: UserDirectory) {}

  async notify(userId: UserId, text: string): Promise<void> {
    const email = await this.users.emailOf(userId);
    await this.mailer.send({ to: email, subject: "Digital Homes", body: text });
  }
}
