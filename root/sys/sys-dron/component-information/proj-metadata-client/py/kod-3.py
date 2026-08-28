FTP_HDR = struct.Struct('<HBBBBBBI')   # seq, session, opcode, size,
                                       # req_opcode, burst_complete, pad, offset
FTP_MAX = 239                          # 251 − 12

OP_TERMINATE, OP_OPEN_RO, OP_BURST = 1, 4, 15
OP_ACK, OP_NAK = 128, 129
ERR_EOF = 6


def ftp_send(link, seq, session, opcode, offset=0, size=0, data=b''):
    payload = FTP_HDR.pack(seq & 0xFFFF, session, opcode, size,
                           0, 0, 0, offset) + data
    payload += b'\x00' * (251 - len(payload))        # поле фіксованої довжини
    link.mav.file_transfer_protocol_send(0, link.target_system, AUTOPILOT,
                                         bytearray(payload))


def ftp_recv(link, want_op, timeout=2.0):
    """Відповідь саме на операцію want_op. Чуже й застаріле — у смітник."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        m = link.recv_match(type='FILE_TRANSFER_PROTOCOL',
                            blocking=True, timeout=0.3)
        if m is None:
            continue
        raw = bytes(m.payload)
        seq, session, opcode, size, req_op, burst_done, _pad, offset = \
            FTP_HDR.unpack_from(raw)
        if req_op != want_op:                        # відгомін давнішого запиту
            continue
        return opcode, size, offset, raw[12:12 + size], burst_done
    return None
