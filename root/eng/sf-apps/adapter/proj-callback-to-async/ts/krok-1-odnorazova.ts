import { readFile } from "node:fs";

// Adaptee: класичний err-first колбек
//   readFile(path, (err, data) => ...)
// Target: щось, що можна await-ити
function readFileAsync(path: string): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    readFile(path, (err, data) => {
      if (err) reject(err);   // гілка помилки колбека → reject
      else resolve(data);     // гілка успіху → resolve
    });
  });
}

// стара функція тепер живе у світі await:
const data = await readFileAsync("./config.json");
