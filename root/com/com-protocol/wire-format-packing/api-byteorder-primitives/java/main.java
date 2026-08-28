import java.nio.ByteBuffer;

static byte[] encHeader(int length, long tUs) {
    ByteBuffer b = ByteBuffer.allocate(16);   // типовий порядок нового буфера — BIG_ENDIAN
    b.putShort((short) 0xa75e);               // magic
    b.put((byte) 2).put((byte) 0);            // ver, flags
    b.putShort((short) length);
    b.putShort((short) 0);                    // rsv
    b.putLong(tUs);
    return b.array();
}

static int lengthOf(byte[] raw) {
    ByteBuffer b = ByteBuffer.wrap(raw);
    return Short.toUnsignedInt(b.getShort(4)); // абсолютне читання: позиція не рухається
}
