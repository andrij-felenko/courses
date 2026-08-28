int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();

    while (1) {
        buzzerUpdate();

        if (ButtonPressed()) SoundOk();      // натиск — бадьорий «ді-дінь»
        if (SensorFailed())  SoundError();   // давач замовк — глухий «дон-дон»
        if (BatteryLow())    SoundWarn();    // сідає батарея — «пік-пік-пік»
        // ...і все це не спиняє цикл ні на мить...
    }
}
