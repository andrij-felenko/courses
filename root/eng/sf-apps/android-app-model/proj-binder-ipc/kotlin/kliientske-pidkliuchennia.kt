package com.example.client

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import android.os.RemoteException
import android.util.Log
import com.example.vault.ISecureVault

class VaultClient(private val context: Context) {

    private var vaultService: ISecureVault? = null
    private var isBound = false

    private val deathRecipient = IBinder.DeathRecipient {
        Log.e("VaultClient", "Віддалений процес сервісу вбито ядром (Process Death)!")
        vaultService = null
        isBound = false
        // Логіка повторного автоматичного підключення за потреби
    }

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            try {
                service?.linkToDeath(deathRecipient, 0)
                vaultService = ISecureVault.Stub.asInterface(service)
                isBound = true
                Log.i("VaultClient", "Успішно з'єднано з віддаленим сервісом")
            } catch (e: RemoteException) {
                Log.e("VaultClient", "Не вдалося прив'язати DeathRecipient", e)
            }
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            // Викликається при неочікуваному розриві зв'язку
            vaultService = null
            isBound = false
        }
    }

    fun connect() {
        val intent = Intent("com.example.vault.ACTION_BIND_VAULT").apply {
            setPackage("com.example.vault") // Явний намір для безпеки зв'язування
        }
        context.bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    fun save(key: String, secretData: ByteArray) {
        val service = vaultService ?: throw IllegalStateException("Сервіс не підключено")
        try {
            service.storeSecret(key, secretData)
        } catch (e: RemoteException) {
            // Перехоплення помилки падіння віддаленого Binder-каналу
            Log.e("VaultClient", "Помилка IPC-транзакції: віддалений сервіс розірвав канал", e)
        }
    }

    fun disconnect() {
        if (isBound) {
            vaultService?.asBinder()?.unlinkToDeath(deathRecipient, 0)
            context.unbindService(connection)
            isBound = false
        }
    }
}
