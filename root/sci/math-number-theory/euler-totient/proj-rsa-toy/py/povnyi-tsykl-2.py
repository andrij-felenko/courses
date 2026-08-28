pub, priv = keygen(1024)               # два прості по 1024 біти → n на 2048
n, e = pub
assert n.bit_length() == 2048

msg = int.from_bytes("Привіт, Ейлере!".encode(), "big")
assert msg < n                         # інакше — тиха підміна, див. нижче

c = encrypt(msg, pub)
back = decrypt(c, priv)
assert back == msg
print(back.to_bytes((back.bit_length() + 7) // 8, "big").decode())
# Привіт, Ейлере!
