void app_main(void)
{
    buzzerBegin();
    while (1) {
        buzzerUpdate();

        if (button_pressed()) sound_ok();      // натиск — бадьорий «ді-дінь»
        if (sensor_failed())  sound_error();   // давач замовк — глухий «дон-дон»
        if (battery_low())    sound_warn();    // сідає батарея — «пік-пік-пік»

        vTaskDelay(pdMS_TO_TICKS(2));   // ...і жоден із цих викликів не чекав...
    }
}
