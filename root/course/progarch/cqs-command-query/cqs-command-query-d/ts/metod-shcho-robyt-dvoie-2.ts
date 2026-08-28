class TelemetryLog {
  private readings: number[] = [];

  // КОМАНДА: змінює стан, нічого не повертає
  append(reading: number): void {
    this.readings.push(reading);
  }

  // ЗАПИТ: відповідає, стану не чіпає
  average(): number {
    if (this.readings.length === 0) return 0;
    const sum = this.readings.reduce((a, b) => a + b, 0);
    return sum / this.readings.length;
  }
}
