function encHeader(length: number, tUs: bigint): Uint8Array {
  const b = new Uint8Array(16);
  const v = new DataView(b.buffer);
  v.setUint16(0, 0xa75e);      // третього аргументу немає → big-endian
  v.setUint8(2, 2);            // ver
  v.setUint8(3, 0);            // flags
  v.setUint16(4, length);
  v.setUint16(6, 0);           // rsv
  v.setBigUint64(8, tUs);      // 64 біти — лише через BigInt
  return b;
}

function lengthOf(raw: Uint8Array): number {
  const v = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
  return v.getUint16(4);       // теж big-endian
}
