def too_slow(elapsed, progress, budget=40.0):
    """Прогноз повного часу за поточним темпом перевищує бюджет?"""
    if progress <= 0.0:
        return False
    return elapsed > 10.0 and progress < 0.5 and elapsed / progress > budget


def ftp_download(link, path, seq=0):
    """Прочитати файл із борту потоковим читанням. Повертає байти або None."""
    name = path.encode('utf-8')
    ftp_send(link, seq, 0, OP_OPEN_RO, size=len(name), data=name)
    reply = ftp_recv(link, OP_OPEN_RO, timeout=3.0)
    if reply is None or reply[0] != OP_ACK:
        return None
    total = struct.unpack('<I', reply[3])[0] if reply[1] == 4 else 0
    if total == 0:
        return None

    buf, seen, have = bytearray(total), {}, 0
    started = time.monotonic()
    seq += 2
    ftp_send(link, seq, 0, OP_BURST, offset=have, size=FTP_MAX)
    last_packet = time.monotonic()

    try:
        while have < total:
            reply = ftp_recv(link, OP_BURST, timeout=0.5)
            now = time.monotonic()

            if reply is not None and reply[0] == OP_ACK:
                _, size, offset, data, burst_done = reply
                buf[offset:offset + size] = data
                seen[offset] = size
                while have in seen:                  # зсунути позначку суцільного
                    have += seen[have]
                last_packet = now
                if burst_done and have < total:      # борт завершив пачку раніше
                    seq += 2
                    ftp_send(link, seq, 0, OP_BURST, offset=have, size=FTP_MAX)
                continue

            if reply is not None and reply[0] == OP_NAK:
                if reply[3][:1] == bytes([ERR_EOF]):
                    break                            # кінець файлу
                return None

            if too_slow(now - started, have / total):
                return None                          # хай спрацює запасна адреса
            if now - last_packet > 2.0:              # пачка загубилася — просити ще
                seq += 2
                ftp_send(link, seq, 0, OP_BURST, offset=have, size=FTP_MAX)
                last_packet = now
    finally:
        ftp_send(link, seq + 2, 0, OP_TERMINATE)     # сесій на борту лічені штуки

    return bytes(buf[:have]) if have >= total else None
