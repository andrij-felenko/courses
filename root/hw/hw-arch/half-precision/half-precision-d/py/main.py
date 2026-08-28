import struct

# Грубе (truncating) перетворення float32 → bfloat16.
# bfloat16 = старші 16 бітів бітового образу float.
def float_to_bf16_truncate(x):
    bits = struct.unpack("<I", struct.pack("<f", x))[0]  # дістати біти float
    return bits >> 16                                    # просто верхня половина слова

def bf16_to_float(b):
    bits = b << 16                                       # дописати 16 молодших нулів
    return struct.unpack("<f", struct.pack("<I", bits))[0]
