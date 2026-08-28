// Піни, куди підключені входи плати ULN2003
const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11;

// Вісім станів half-step. Рядок — один такт; стовпці — IN1..IN4.
// 1 = обмотку під струмом (вхід HIGH), 0 = знеструмлено (LOW).
const int seq[8][4] = {
  {1, 0, 0, 0},   // крок 1
  {1, 1, 0, 0},   // крок 2
  {0, 1, 0, 0},   // крок 3
  {0, 1, 1, 0},   // крок 4
  {0, 0, 1, 0},   // крок 5
  {0, 0, 1, 1},   // крок 6
  {0, 0, 0, 1},   // крок 7
  {1, 0, 0, 1},   // крок 8
};

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}
