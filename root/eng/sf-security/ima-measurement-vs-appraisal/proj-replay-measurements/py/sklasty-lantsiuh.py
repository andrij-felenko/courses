def replay(blob, algo):
    h = lambda b: hashlib.new(algo, b).digest()
    dlen = hashlib.new(algo).digest_size
    pcr, trace = b"\x00" * dlen, {}
    broken, violations = [], []
    for n, _idx, digest, name, body in entries(blob, dlen):
        if digest == b"\x00" * dlen:            # порушення: у список ідуть нулі,
            violations.append((n, name))        # а в чип — одиниці
            digest = b"\xff" * dlen
        elif digest != h(body):
            broken.append((n, name))            # запис не сходиться сам із собою
        pcr = h(pcr + digest)
        trace[pcr] = n
    return trace, broken, violations


def main(path, quoted_hex, algo="sha1"):
    trace, broken, violations = replay(open(path, "rb").read(), algo)
    total = max(trace.values(), default=0)

    for n, name in broken:
        print(f"запис {n} ({name}): хеш запису не відповідає власним даним")
    for n, name in violations:
        print(f"запис {n} ({name}): порушення — регістр отруєно навмисне")

    at = trace.get(bytes.fromhex(quoted_hex))
    if at is None:
        print("знімок із чипа не збігається з жодним станом ланцюга — журналу вірити не можна")
    elif at == total:
        print(f"збіг на останньому записі: чип підтверджує всі {total} рядків")
    else:
        print(f"збіг на записі {at}: рядки {at + 1}..{total} дописано вже після знімка")


if __name__ == "__main__":
    main(*sys.argv[1:])
