// Стан автомата корутини
enum State {
  Start = 0,
  AfterProfile = 1,
  AfterBalance = 2,
  Completed = 3
}

class CalculateTotalBalanceStateMachine {
  // Кадр збереження локального стану (Heap Frame)
  public state: State = State.Start;
  private userId: string;
  private profile: { accountIds: string[] } | null = null;
  private total: number = 0;
  private loopIndex: number = 0;

  // Вихідний проміс для повернення результату викликачу
  public promise: Promise<number>;
  private resolve!: (val: number) => void;
  private reject!: (err: unknown) => void;

  constructor(userId: string) {
    this.userId = userId;
    this.promise = new Promise<number>((res, rej) => {
      this.resolve = res;
      this.reject = rej;
    });
  }

  // Головний крок виконання автомата (Resume Dispatcher)
  public resume(result?: unknown, error?: unknown): void {
    try {
      if (error) {
        // Якщо надійшла помилка від асинхронної дії — переходимо в блок catch
        throw error;
      }

      while (this.state !== State.Completed) {
        switch (this.state) {
          case State.Start: {
            this.state = State.AfterProfile;
            const promise = fetchProfile(this.userId);
            // Призупинення: підписуємо наш же автомат на продовження
            promise.then(
              (res) => this.resume(res, undefined),
              (err) => this.resume(undefined, err)
            );
            return; // Звільняємо системний потік для циклу подій
          }

          case State.AfterProfile: {
            this.profile = result as { accountIds: string[] };
            this.total = 0;
            this.loopIndex = 0;
            this.state = State.AfterBalance;

            // Перевірка умови циклу
            if (this.loopIndex >= this.profile.accountIds.length) {
              this.state = State.Completed;
              this.resolve(this.total);
              return;
            }

            const accId = this.profile.accountIds[this.loopIndex];
            const promise = fetchAccountBalance(accId);
            promise.then(
              (res) => this.resume(res, undefined),
              (err) => this.resume(undefined, err)
            );
            return;
          }

          case State.AfterBalance: {
            const balance = result as number;
            this.total += balance;
            this.loopIndex++;

            // Наступна ітерація або завершення циклу
            if (this.loopIndex < this.profile!.accountIds.length) {
              const nextAccId = this.profile!.accountIds[this.loopIndex];
              const promise = fetchAccountBalance(nextAccId);
              promise.then(
                (res) => this.resume(res, undefined),
                (err) => this.resume(undefined, err)
              );
              return;
            }

            this.state = State.Completed;
            this.resolve(this.total);
            return;
          }
        }
      }
    } catch (err) {
      // Імітація блоку catch(err)
      console.error("Помилка розрахунку в автоматі:", err);
      this.state = State.Completed;
      this.resolve(0); // Безпечне значення за замовчуванням
    }
  }
}

// Функція-обгортка для виклику децукрованого автомата
function calculateTotalBalanceDesugared(userId: string): Promise<number> {
  const machine = new CalculateTotalBalanceStateMachine(userId);
  machine.resume(); // Запуск першого кроку
  return machine.promise;
}
