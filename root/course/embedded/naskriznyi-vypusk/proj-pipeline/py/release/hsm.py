# -*- coding: utf-8 -*-
"""Ворота 5 — підпис дайджесту поза раннером.

Закритий ключ у пам'ять раннера не потрапляє ніколи: назовні йде рівно
32 байти хешу, назад приходить 64 байти сирого ECDSA P-256 (r||s).

Бекенди:
  RELEASE_SIGNER=pkcs11      — бойовий HSM через pkcs11-tool (OpenSC);
  RELEASE_SIGNER=dev-openssl — стенд розробника, ключ у файлі (типово).
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from .config import DIGEST_LEN, SIGNATURE_LEN, fail, log

STAGE = "G5-SIGN"

_BACKEND = os.environ.get("RELEASE_SIGNER", "dev-openssl")
_DEV_KEY = Path(os.environ.get("RELEASE_DEV_KEY", ".release-dev-key.pem"))


def step_3_mock_hsm_sign(digest_bytes: bytes, key_id: str) -> bytes:
    """Єдина точка, де народжується підпис."""
    if len(digest_bytes) != DIGEST_LEN:
        fail(STAGE, f"на підпис подано {len(digest_bytes)} Б замість {DIGEST_LEN}")

    log(STAGE, f"дайджест {digest_bytes.hex()[:16]}… → {_BACKEND} [ключ {key_id}]")
    if _BACKEND == "pkcs11":
        signature = _sign_pkcs11(digest_bytes, key_id)
    elif _BACKEND == "dev-openssl":
        signature = _sign_dev_openssl(digest_bytes)
    else:
        fail(STAGE, f"невідомий бекенд підпису '{_BACKEND}'")

    if len(signature) != SIGNATURE_LEN:
        fail(STAGE, f"підпис {len(signature)} Б замість {SIGNATURE_LEN}: "
                    "бекенд віддав не сирі r||s")
    return signature


def _sign_pkcs11(digest: bytes, key_id: str) -> bytes:
    module = os.environ.get("HSM_PKCS11_MODULE")
    if not module:
        fail(STAGE, "RELEASE_SIGNER=pkcs11, але HSM_PKCS11_MODULE не задано")

    with tempfile.TemporaryDirectory() as tmp:
        din = Path(tmp) / "digest.bin"
        dout = Path(tmp) / "signature.raw"
        din.write_bytes(digest)
        cmd = ["pkcs11-tool", "--module", module, "--sign",
               "--mechanism", "ECDSA", "--label", key_id,
               "--input-file", str(din), "--output-file", str(dout)]
        pin = os.environ.get("HSM_PIN")
        if pin:
            cmd += ["--pin", pin]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            fail(STAGE, f"pkcs11-tool: {res.stderr.strip()}")
        # Механізм CKM_ECDSA віддає рівно r||s, без обгортки ASN.1.
        return dout.read_bytes()


def _sign_dev_openssl(digest: bytes) -> bytes:
    key = _ensure_dev_key()
    with tempfile.TemporaryDirectory() as tmp:
        din = Path(tmp) / "digest.bin"
        dout = Path(tmp) / "signature.der"
        din.write_bytes(digest)
        # pkeyutl підписує вміст файла як готовий дайджест — саме те, що
        # робить HSM: жодного повторного хешування.
        res = subprocess.run(
            ["openssl", "pkeyutl", "-sign", "-inkey", str(key),
             "-in", str(din), "-out", str(dout)],
            capture_output=True, text=True)
        if res.returncode != 0:
            fail(STAGE, f"openssl pkeyutl: {res.stderr.strip()}")
        return _der_to_raw_rs(dout.read_bytes())


def _ensure_dev_key() -> Path:
    if _DEV_KEY.exists():
        return _DEV_KEY
    log(STAGE, f"УВАГА: створюю ключ стенда {_DEV_KEY}. "
               "Образи, підписані ним, у поле не йдуть!")
    res = subprocess.run(
        ["openssl", "ecparam", "-name", "prime256v1", "-genkey",
         "-noout", "-out", str(_DEV_KEY)],
        capture_output=True, text=True)
    if res.returncode != 0:
        fail(STAGE, f"openssl ecparam: {res.stderr.strip()}")
    _DEV_KEY.chmod(0o600)
    return _DEV_KEY


def _der_to_raw_rs(der: bytes) -> bytes:
    """SEQUENCE { INTEGER r, INTEGER s } → 64 байти r||s.

    ASN.1 зберігає числа зі знаком і без провідних нулів, тож r і s бувають
    і 33-байтні (доданий 0x00), і коротші за 32. Завантажувач чекає рівно
    два 32-байтні великі числа.
    """
    def read_integer(buf: bytes, pos: int) -> tuple[int, int]:
        if buf[pos] != 0x02:
            fail(STAGE, "у підписі очікувався ASN.1 INTEGER")
        length = buf[pos + 1]
        if length & 0x80:
            fail(STAGE, "довга форма довжини в підписі не підтримується")
        value = int.from_bytes(buf[pos + 2:pos + 2 + length], "big")
        return value, pos + 2 + length

    if len(der) < 8 or der[0] != 0x30:
        fail(STAGE, "openssl віддав не SEQUENCE — це не підпис ECDSA")
    body_len = der[1]
    if body_len & 0x80 or body_len + 2 != len(der):
        fail(STAGE, "довжина ASN.1 не збігається з розміром відповіді")

    r, pos = read_integer(der, 2)
    s, pos = read_integer(der, pos)
    if pos != len(der):
        fail(STAGE, "у підписі лишилися зайві байти")
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def export_public_key(dest: Path) -> Path | None:
    """Кладе поруч із бандлом відкритий ключ стенда (65 Б, SEC1 uncompressed).

    Бойовий ключ так не експортується: він прошитий у завантажувачі як
    корінь довіри, і бандл на нього ніяк не впливає.
    """
    if _BACKEND != "dev-openssl":
        log(STAGE, "бойовий корінь довіри вже в завантажувачі — не експортую")
        return None

    res = subprocess.run(
        ["openssl", "ec", "-in", str(_ensure_dev_key()),
         "-pubout", "-outform", "DER"],
        capture_output=True)
    if res.returncode != 0:
        fail(STAGE, f"openssl ec -pubout: {res.stderr.decode(errors='replace').strip()}")

    spki = res.stdout
    # У SPKI для P-256 точка лежить у хвості: 65 байтів, що починаються 0x04.
    point = spki[-65:]
    if len(point) != 65 or point[0] != 0x04:
        fail(STAGE, "не знайшов непаковану точку в SubjectPublicKeyInfo")
    dest.write_bytes(point)
    log(STAGE, f"відкритий ключ стенда → {dest.name}")
    return dest
