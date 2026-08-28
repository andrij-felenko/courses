from dataclasses import dataclass, field

@dataclass
class SbusData:
    ch: list = field(default_factory=lambda: [0] * 16)  # сирі 0..2047
    ch17: int = 0        # 0/1
    ch18: int = 0        # 0/1
    frame_lost: int = 0  # 0/1
    failsafe: int = 0    # 0/1

def sbus_read_flags(flags, out):
    out.ch17       = 1 if flags & 0x01 else 0
    out.ch18       = 1 if flags & 0x02 else 0
    out.frame_lost = 1 if flags & 0x04 else 0
    out.failsafe   = 1 if flags & 0x08 else 0
