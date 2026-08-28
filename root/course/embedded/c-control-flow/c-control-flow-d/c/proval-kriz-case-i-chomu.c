switch (key) {
    case '0': case '1': case '2': case '3': case '4':
    case '5': case '6': case '7': case '8': case '9':
        handle_digit(key);   // сюди «протікають» усі десять міток-цифр
        break;
    case '\n':
    case '\r':
        submit();            // і Enter, і повернення каретки — те саме
        break;
    default:
        beep_error();
}
