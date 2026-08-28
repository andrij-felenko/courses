def ip_checksum(hdr: bytes) -> int:
    hdr = hdr[:10] + b"\x00\x00" + hdr[12:]          # занулити поле суми
    return ~fold(sum_words(hdr)) & 0xFFFF


def udp_checksum_v4(src: bytes, dst: bytes, udp: bytes) -> int:
    udp = udp[:6] + b"\x00\x00" + udp[8:]            # занулити поле суми
    s = pseudo_v4(src, dst, IPPROTO_UDP, len(udp))
    return (~fold(sum_words(udp, s)) & 0xFFFF) or 0xFFFF     # трюк UDP


def tcp_checksum_v4(src: bytes, dst: bytes, tcp: bytes) -> int:
    tcp = tcp[:16] + b"\x00\x00" + tcp[18:]          # поле TCP — на зсуві 16
    s = pseudo_v4(src, dst, IPPROTO_TCP, len(tcp))
    return ~fold(sum_words(tcp, s)) & 0xFFFF         # 0x0000 у TCP — законне


def udp_verify_v4(src: bytes, dst: bytes, udp: bytes) -> bool:
    if udp[6:8] == b"\x00\x00":
        return True                                  # в IPv4 нуль = «суми нема»
    s = pseudo_v4(src, dst, IPPROTO_UDP, len(udp))
    return fold(sum_words(udp, s)) == 0xFFFF
