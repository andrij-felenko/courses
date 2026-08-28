def to_stored(row):
    return {"status": row["response_status"],
            "headers": json.loads(row["response_headers"] or "{}"),
            "body": bytes(row["response_body"])}

def send(s, replayed):
    headers = dict(s["headers"])
    if replayed:
        headers["Idempotent-Replayed"] = "true"   # чесно кажемо: це відтворення
    return raw_response(status=s["status"], headers=headers, body=s["body"])  # ті самі байти
