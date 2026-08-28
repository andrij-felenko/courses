// Віддати файл name зі статичної теки, порціями через потік.
const fs = require("fs");
const path = require("path");

const TYPES = { ".html": "text/html", ".css": "text/css",
                ".js": "application/javascript" };

function sendFileFromFs(res, name) {
  const full = path.join("/spiffs", name);
  if (!fs.existsSync(full)) {                   // нема файлу — чесний 404
    res.status(404).end();
    return;
  }

  const ext = path.extname(name);               // тип за розширенням
  res.type(TYPES[ext] || "text/plain");

  // ПОРЦІЯМИ: потік читає файл шматками, не тримаючи його в пам'яті цілком
  fs.createReadStream(full, { highWaterMark: 512 }).pipe(res);
}
