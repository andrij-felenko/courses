int main(void)
{
	init();          // налаштувати таймери, АЦП, лічильник millis() — усе «нутро»

	initVariant();   // гак для конкретної плати (порожній, якщо нема потреби)

#if defined(USBCON)
	USBDevice.attach();   // на чипах із власним USB (Leonardo) — підняти USB-стек
#endif

	setup();         // ← ТВОЯ підготовка: один раз

	for (;;) {       // вічний цикл — серце мікроконтролера
		loop();                        // ← ТВОЯ робота: знову і знову
		if (serialEventRun) serialEventRun();
	}

	return 0;        // сюди не дійдемо ніколи
}
