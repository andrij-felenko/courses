package com.example.vault

import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Binder
import android.os.IBinder
import android.os.Process
import android.os.RemoteException
import java.util.concurrent.ConcurrentHashMap

class SecureVaultService : Service() {

    private val storage = ConcurrentHashMap<String, ByteArray>()

    private val binder = object : ISecureVault.Stub() {
        override fun storeSecret(key: String, payload: ByteArray) {
            enforceSignaturePermission()
            if (payload.size > 256 * 1024) {
                throw IllegalArgumentException("Розмір корисного навантаження перевищує 256 КБ")
            }
            storage[key] = payload
        }

        override fun retrieveSecret(key: String): ByteArray {
            enforceSignaturePermission()
            return storage[key] ?: ByteArray(0)
        }

        override fun getCallerProcessUid(): Int {
            return Binder.getCallingUid()
        }

        private fun enforceSignaturePermission() {
            val callingUid = Binder.getCallingUid()
            val callingPid = Binder.getCallingPid()

            // Якщо виклик локальний (у межах власного процесу), перевірку пропускаємо
            if (callingUid == Process.myUid()) {
                return
            }

            // 1. Перевірка статичного або динамічного дозволу
            val permCheck = checkCallingOrSelfPermission(
                "com.example.vault.permission.ACCESS_VAULT"
            )
            if (permCheck != PackageManager.PERMISSION_GRANTED) {
                throw SecurityException(
                    "Процес UID $callingUid (PID $callingPid) не має дозволу ACCESS_VAULT"
                )
            }

            // 2. Додаткова строга верифікація збігу сертифіката підпису (signature protection)
            val match = packageManager.checkSignatures(callingUid, Process.myUid())
            if (match != PackageManager.SIGNATURE_MATCH) {
                throw SecurityException(
                    "Підпис клієнтського застосунку (UID $callingUid) не збігається з підписом сховища"
                )
            }
        }
    }

    override fun onBind(intent: Intent?): IBinder {
        return binder
    }
}
