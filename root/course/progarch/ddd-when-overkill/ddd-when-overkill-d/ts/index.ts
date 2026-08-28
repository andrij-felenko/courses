// Ядро: правило живе в одному захищеному місці, названо мовою предмета
class Room {
  private heater = false;
  private cooler = false;

  startHeating(): void {
    if (this.cooler)                       // інваріант безпеки — тут і тільки тут
      throw new DomainError("не можна гріти й холодити кімнату разом");
    this.heater = true;
  }
}

// Допоміжне: реєстр пристроїв — голий запис, і це правильно
interface Device { id: string; room: string; name: string; }
// «додати» і «перейменувати» — то й уся «логіка»; багатити тут нема чого
