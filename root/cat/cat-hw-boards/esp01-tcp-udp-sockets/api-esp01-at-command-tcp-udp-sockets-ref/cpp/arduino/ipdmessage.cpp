// C++: Парсинг заголовка асинхронної події +IPD під Arduino
#include <Arduino.h>

struct IPDMessage {
  int linkId;
  int length;
  String payload;
};

bool parseIPD(String rxLine, IPDMessage &msg) {
  if (!rxLine.startsWith("+IPD,")) return false;
  
  int firstComma = rxLine.indexOf(',');
  int colonIndex = rxLine.indexOf(':');
  int secondComma = rxLine.indexOf(',', firstComma + 1);
  
  if (secondComma != -1 && secondComma < colonIndex) {
    // Багатоканальний режим +IPD,id,len:data
    msg.linkId = rxLine.substring(firstComma + 1, secondComma).toInt();
    msg.length = rxLine.substring(secondComma + 1, colonIndex).toInt();
  } else {
    // Одиночний режим +IPD,len:data
    msg.linkId = 0;
    msg.length = rxLine.substring(firstComma + 1, colonIndex).toInt();
  }
  msg.payload = rxLine.substring(colonIndex + 1);
  return true;
}
