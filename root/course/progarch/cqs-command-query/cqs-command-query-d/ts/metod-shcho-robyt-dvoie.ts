class TelemetryLog {
  private readings: number[] = [];

  // робить двоє: І дописує показник, І повертає нове середнє
  append(reading: number): number {
    this.readings.push(reading);
    const sum = this.readings.reduce((a, b) => a + b, 0);
    return sum / this.readings.length;
  }
}
