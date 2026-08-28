# storage.py — світлини живуть в об'єктному сховищі (S3-сумісному), не на диску.
import boto3
from config import config

s3 = boto3.client(
    "s3",
    endpoint_url=config.S3_ENDPOINT,           # адреса сховища — із середовища
    aws_access_key_id=config.S3_KEY,
    aws_secret_access_key=config.S3_SECRET,
)
BUCKET = config.S3_BUCKET

def put_photo(user_id: int, name: str, data) -> str:
    key = f"{user_id}/{name}"                   # ключ об'єкта, не шлях на диску
    s3.upload_fileobj(data, BUCKET, key)        # ← у СПІЛЬНЕ сховище
    return key

def photo_url(user_id: int, name: str) -> str:
    key = f"{user_id}/{name}"
    # Підписане тимчасове посилання — клієнт забирає файл ПРЯМО зі сховища,
    # застосунок навіть не гонить байти крізь себе.
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=300
    )
