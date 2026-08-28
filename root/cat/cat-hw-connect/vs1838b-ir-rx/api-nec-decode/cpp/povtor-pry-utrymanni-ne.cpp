if (IrReceiver.decode()) {
    if (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT) {
        // кнопку ТРИМАЮТЬ — команда та сама, що останнього повного кадру
        handleHeld(lastCommand);           // напр. плавно міняти гучність далі
    } else {
        lastCommand = IrReceiver.decodedIRData.command;   // новий повний кадр — запам'ятати команду
        handlePress(lastCommand);
    }
    IrReceiver.resume();
}
