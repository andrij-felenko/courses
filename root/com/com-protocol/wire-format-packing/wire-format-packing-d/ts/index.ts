function encHeader(len: number, tUs: bigint): Uint8Array {
  const b = new Uint8Array(16);
  const v = new DataView(b.buffer);
  v.setUint16(0, 0xa75e);   // DataView за замовчуванням старший байт першим
  v.setUint8(2, 2);         // ver
  v.setUint8(3, 0);         // flags
  v.setUint16(4, len);
  v.setUint16(6, 0);        // rsv
  v.setBigUint64(8, tUs);
  return b;
}
