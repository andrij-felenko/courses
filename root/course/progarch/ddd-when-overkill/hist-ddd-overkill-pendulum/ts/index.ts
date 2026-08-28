// на вигляд — доменна модель: клас названо мовою предмета
class Room {
  heater = false;
  cooler = false;
  // ...самі поля з гетерами/сетерами, жодного правила всередині
}

// а все правило — деінде, у службі, що смикає чужі поля
class RoomService {
  startHeating(room: Room): void {
    if (room.cooler) throw new Error("не можна гріти й холодити разом");
    room.heater = true;               // інваріант стереже хтось інший, не сама кімната
  }
}
