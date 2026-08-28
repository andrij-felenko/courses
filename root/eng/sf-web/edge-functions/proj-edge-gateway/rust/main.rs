// ============================================================================
// Edge API Gateway: Rust (WebAssembly / Fastly Compute / WASI)
// ============================================================================

use fastly::http::{header, Method, StatusCode};
use fastly::{Error, Request, Response};
use hmac::{Hmac, Mac};
use jwt::VerifyWithKey;
use sha2::Sha256;
use std::collections::BTreeMap;
use std::time::{SystemTime, UNIX_EPOCH};

type HmacSha256 = Hmac<Sha256>;

fn hash_fnv1a(input: &str) -> u32 {
    let mut hash: u32 = 0x811c9dc5;
    for byte in input.bytes() {
        hash ^= byte as u32;
        hash = hash.wrapping_mul(0x01000193);
    }
    hash
}

fn verify_jwt(token: &str, secret: &[u8]) -> Option<String> {
    let key: HmacSha256 = HmacSha256::new_from_slice(secret).ok()?;
    let claims: BTreeMap<String, String> = token.verify_with_key(&key).ok()?;

    if let Some(exp_str) = claims.get("exp") {
        if let Ok(exp_sec) = exp_str.parse::<u64>() {
            let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
            if exp_sec < now {
                return None; // Термін придатності вичерпано
            }
        }
    }

    claims.get("sub").cloned()
}

#[fastly::main]
fn main(mut req: Request) -> Result<Response, Error> {
    // Пропускаємо перевірку здоров'я
    if req.get_path() == "/healthz" {
        return Ok(Response::from_status(StatusCode::OK).with_body("healthy\n"));
    }

    // 1. Валідація JWT
    let auth_header = req.get_header(header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok());

    let token = match auth_header {
        Some(h) if h.starts_with("Bearer ") => &h[7..],
        _ => {
            return Ok(Response::from_status(StatusCode::UNAUTHORIZED)
                .with_header(header::CONTENT_TYPE, "application/json")
                .with_body("{\"error\":\"Missing or malformed Authorization header\"}\n"));
        }
    };

    let secret = std::env::var("JWT_SECRET").unwrap_or_else(|_| "secret_key".to_string());
    let user_id = match verify_jwt(token, secret.as_bytes()) {
        Some(id) => id,
        None => {
            return Ok(Response::from_status(StatusCode::UNAUTHORIZED)
                .with_header(header::CONTENT_TYPE, "application/json")
                .with_body("{\"error\":\"Invalid or expired JWT token\"}\n"));
        }
    };

    // 2. A/B спліт на основі cookie або user_id
    let hash = hash_fnv1a(&user_id);
    let variant = if (hash % 100) < 80 { "control-v1" } else { "experiment-v2" };

    // 3. Збагачення заголовків для бекенду
    req.set_header("X-User-Id", user_id);
    req.set_header("X-AB-Variant", variant);

    // 4. Відправка запиту на бекенд
    let mut upstream_resp = req.send("origin_backend")?;

    // 5. Потокова модифікація заголовків безпеки
    upstream_resp.set_header("X-Edge-Runtime", "Wasm-Fastly");
    upstream_resp.set_header("X-AB-Variant", variant);
    upstream_resp.set_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains");

    Ok(upstream_resp)
}
