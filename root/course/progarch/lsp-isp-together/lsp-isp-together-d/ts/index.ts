interface IDevice {
  read(): number;          // прочитати вимір
  turnOn(): void;          // увімкнути
  turnOff(): void;         // вимкнути
  lock(): void;            // замкнути
  startStream(): string;   // почати відеопотік
}

class TempSensor implements IDevice {
  read(): number { return this.celsius; }           // це він уміє
  turnOn():  void { throw new Error("датчик не вмикається"); }
  turnOff(): void { throw new Error("датчик не вимикається"); }
  lock():    void { throw new Error("датчик не замикається"); }
  startStream(): string { throw new Error("у датчика немає камери"); }
}
