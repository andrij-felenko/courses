// storage.ts — світлини в S3-сумісному об'єктному сховищі.
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { config } from "./config";

const s3 = new S3Client({
  endpoint: config.S3_ENDPOINT,       // адреса сховища — із середовища
  credentials: { accessKeyId: config.S3_KEY, secretAccessKey: config.S3_SECRET },
  region: "auto",
});
const BUCKET = config.S3_BUCKET;

export async function putPhoto(userId: number, name: string, body: Buffer): Promise<string> {
  const key = `${userId}/${name}`;    // ключ об'єкта, не шлях на диску
  await s3.send(new PutObjectCommand({ Bucket: BUCKET, Key: key, Body: body }));
  return key;                          // ← у СПІЛЬНЕ сховище
}

export async function photoUrl(userId: number, name: string): Promise<string> {
  const key = `${userId}/${name}`;
  // Підписане тимчасове посилання — клієнт тягне файл прямо зі сховища.
  return getSignedUrl(s3, new GetObjectCommand({ Bucket: BUCKET, Key: key }), { expiresIn: 300 });
}
