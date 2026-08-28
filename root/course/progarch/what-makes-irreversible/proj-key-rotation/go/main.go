package issue

import (
	"crypto/ed25519"
	"encoding/binary"
	"time"
)

const (
	roleOp   = 0
	roleRoot = 1
)

// Канонічна серіалізація — МУСИТЬ збігатися з прошивкою побайтово.
func serializeGrant(deviceID, kid uint32, notAfter uint64, nonce [16]byte) []byte {
	b := make([]byte, 0, 34)
	b = append(b, 1, 1) // version=1, type=1 (дозвіл на відкриття)
	b = binary.BigEndian.AppendUint32(b, deviceID)
	b = binary.BigEndian.AppendUint32(b, kid)
	b = binary.BigEndian.AppendUint64(b, notAfter)
	return append(b, nonce[:]...)
}

// ГАРЯЧИЙ шлях: операційний ключ підписує короткочасний дозвіл. Робиться
// щоразу, коли власник відчиняє замок; приватний ключ — у пам'яті сервісу.
func SignGrant(opPriv ed25519.PrivateKey, kid, deviceID uint32, nonce [16]byte) []byte {
	body := serializeGrant(deviceID, kid, uint64(time.Now().Add(2*time.Minute).Unix()), nonce)
	return append(body, ed25519.Sign(opPriv, body)...)
}

func serializeAddKey(signerKid, targetKid uint32, role byte, nb, na uint64, pub []byte) []byte {
	b := make([]byte, 0, 59)
	b = append(b, 1, 2) // version=1, type=2 (додати ключ)
	b = binary.BigEndian.AppendUint32(b, signerKid)
	b = binary.BigEndian.AppendUint32(b, targetKid)
	b = append(b, role)
	b = binary.BigEndian.AppendUint64(b, nb)
	b = binary.BigEndian.AppendUint64(b, na)
	return append(b, pub...) // 32 байти
}

// Signer ходить у HSM — приватний КОРІНЬ звідси не виходить.
type Signer interface{ Sign(msg []byte) []byte }

// РІДКІСНИЙ шлях: корінь підписує «додати операційний ключ #target».
// Викликається раз на ротацію, вручну, з доступом до HSM.
func IssueAddOpKey(root Signer, rootKid, targetKid uint32, pub []byte, nb, na uint64) []byte {
	body := serializeAddKey(rootKid, targetKid, roleOp, nb, na, pub)
	return append(body, root.Sign(body)...)
}
