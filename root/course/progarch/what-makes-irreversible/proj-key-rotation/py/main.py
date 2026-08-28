import struct, time
from typing import Callable
from nacl.signing import SigningKey

ROLE_OP, ROLE_ROOT = 0, 1

def serialize_grant(device_id: int, kid: int, not_after: int, nonce: bytes) -> bytes:
    # Канонічна серіалізація — МУСИТЬ збігатися з прошивкою побайтово.
    # ">BBIIQ" = version|type|device_id|kid|not_after (18 б) + nonce (16 б) = 34 б.
    return struct.pack(">BBIIQ", 1, 1, device_id, kid, not_after) + nonce

def sign_grant(op_priv: SigningKey, kid: int, device_id: int, nonce: bytes) -> bytes:
    # ГАРЯЧИЙ шлях: операційний ключ підписує короткочасний дозвіл.
    body = serialize_grant(device_id, kid, int(time.time()) + 120, nonce)
    return body + op_priv.sign(body).signature      # 34 + 64

def serialize_add_key(signer_kid, target_kid, role, nb, na, pub) -> bytes:
    # ">BBIIBQQ" = version|type|signer|target|role|nb|na (27 б) + pub (32 б) = 59 б.
    return struct.pack(">BBIIBQQ", 1, 2, signer_kid, target_kid, role, nb, na) + pub

def issue_add_op_key(root_sign: Callable[[bytes], bytes],
                     root_kid, target_kid, pub, nb, na) -> bytes:
    # РІДКІСНИЙ шлях: корінь підписує «додати операційний ключ».
    # root_sign ходить у HSM — приватний корінь звідси не виходить.
    body = serialize_add_key(root_kid, target_kid, ROLE_OP, nb, na, pub)
    return body + root_sign(body)
