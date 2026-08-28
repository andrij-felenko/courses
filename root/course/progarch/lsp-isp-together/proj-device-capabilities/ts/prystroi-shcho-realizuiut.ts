class TempSensor implements Readable {
  constructor(private celsius: number) {}
  read(): number { return this.celsius; }          // це все, що він уміє
}

class SmartSocket implements Readable, Switchable {
  private on = false;
  constructor(private watts = 60) {}
  read(): number  { return this.on ? this.watts : 0; }  // спожита потужність, Вт
  turnOn(): void  { this.on = true; }
  turnOff(): void { this.on = false; }
  isOn(): boolean { return this.on; }
}

class DoorLock implements Lockable {
  private locked = false;
  lock(): void        { this.locked = true; }
  unlock(): void      { this.locked = false; }
  isLocked(): boolean { return this.locked; }
}

class Camera implements Streamable {
  private streaming = false;
  startStream(): string { this.streaming = true; return "rtsp://dh/cam/live"; }
  stopStream(): void    { this.streaming = false; }
}
