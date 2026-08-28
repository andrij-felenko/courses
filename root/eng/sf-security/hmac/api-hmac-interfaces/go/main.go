package main

import (
    "crypto/hmac"
    "crypto/sha256"
)

// Генерація HMAC-SHA256 підпису
func Sign(key, data []byte) []byte {
    mac := hmac.New(sha256.New, key)
    mac.Write(data)
    return mac.Sum(nil)
}

// Захищена верифікація через hmac.Equal (вбудований константний час)
func Verify(key, data, expectedMAC []byte) bool {
    actualMAC := Sign(key, data)
    return hmac.Equal(actualMAC, expectedMAC)
}
