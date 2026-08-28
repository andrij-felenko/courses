import { createServer } from "node:http";
import { scryptSync } from "node:crypto";

createServer((req, res) => {
  if (req.url === "/health") {
    res.end("ok");                                 // легкий обробник — миттю
  } else {
    scryptSync("pw", "salt", 64, { N: 2 ** 17 });  // ОТРУТА: ~200 мс на єдинім потоці
    res.end("done");
  }
}).listen(3000);
// Поки рахується scrypt, КОЖЕН паралельний /health застигає: потік один.
