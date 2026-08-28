// Десеріалізація: 8 байтів дроту → об'єкт полів. littleEndian=true;
// getInt16 повертає знакове (temperature ×100).
function unpackSensor(data) {
  const dv = new DataView(data.buffer, data.byteOffset, data.byteLength);
  return {
    msgId:       dv.getUint8(0),
    timestamp:   dv.getUint32(1, true),
    temperature: dv.getInt16(5, true),
    flags:       dv.getUint8(7),
  };
}
