switch (command) {
    case CMD_START:
        motor_start();
        break;              // без break потік «протече» в наступний case
    case CMD_STOP:
        motor_stop();
        break;
    default:
        log_unknown(command);   // жоден case не збігся
}
