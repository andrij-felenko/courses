// Серіалізація: поля → рівно 8 байтів дроту. Порядок і розрядність — наші.
// DataView з прапорцем littleEndian=true кладе молодший байт уперед;
// setInt16 знакове (temperature ×100).
function packSensor(msgId, timestamp, temperature, flags) {
  const buf = new Uint8Array(8);
  const dv = new DataView(buf.buffer);
  dv.setUint8(0, msgId);                 // 1 байт
  dv.setUint32(1, timestamp, true);      // 4 байти
  dv.setInt16(5, temperature, true);     // 2 байти
  dv.setUint8(7, flags);                 // 1 байт
  return buf;
}
