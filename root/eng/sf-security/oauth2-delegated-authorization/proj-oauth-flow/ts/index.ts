import crypto from "crypto";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  scope?: string;
}

export class OAuthClient {
  private readonly authServerUrl: string;
  private readonly authorizeEndpoint: string;
  private readonly tokenEndpoint: string;
  private readonly clientId: string;
  private readonly clientSecret?: string;
  private readonly redirectUri: string;
  private readonly clockSkewSeconds: number;

  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private expiresAt: number = 0;

  private pendingVerifier: string | null = null;
  private pendingState: string | null = null;
  private refreshPromise: Promise<TokenResponse> | null = null;

  constructor(options: {
    authServerUrl: string;
    clientId: string;
    redirectUri: string;
    clientSecret?: string;
    clockSkewSeconds?: number;
  }) {
    this.authServerUrl = options.authServerUrl.replace(/\/+$/, "");
    this.authorizeEndpoint = `${this.authServerUrl}/oauth/authorize`;
    this.tokenEndpoint = `${this.authServerUrl}/oauth/token`;
    this.clientId = options.clientId;
    this.clientSecret = options.clientSecret;
    this.redirectUri = options.redirectUri;
    this.clockSkewSeconds = options.clockSkewSeconds ?? 60;
  }

  private static base64UrlEncode(buffer: Buffer): string {
    return buffer
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  }

  public generatePkcePair(): { verifier: string; challenge: string } {
    const verifier = OAuthClient.base64UrlEncode(crypto.randomBytes(64));
    const hash = crypto.createHash("sha256").update(verifier, "ascii").digest();
    const challenge = OAuthClient.base64UrlEncode(hash);
    return { verifier, challenge };
  }

  public createAuthorizationUrl(scopes: string[]): string {
    const { verifier, challenge } = this.generatePkcePair();
    const state = OAuthClient.base64UrlEncode(crypto.randomBytes(32));

    this.pendingVerifier = verifier;
    this.pendingState = state;

    const params = new URLSearchParams({
      response_type: "code",
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      scope: scopes.join(" "),
      state,
      code_challenge: challenge,
      code_challenge_method: "S256"
    });

    return `${this.authorizeEndpoint}?${params.toString()}`;
  }

  public async handleCallback(queryParams: Record<string, string>): Promise<TokenResponse> {
    if (queryParams.error) {
      throw new Error(`Сервер відхилив авторизацію: ${queryParams.error} (${queryParams.error_description ?? ""})`);
    }

    const state = queryParams.state ?? "";
    if (!this.pendingState || !crypto.timingSafeEqual(Buffer.from(this.pendingState), Buffer.from(state))) {
      throw new Error("Атака підробки міжсайтового запиту: параметр state не збігається");
    }

    const code = queryParams.code;
    if (!code) {
      throw new Error("Відповідь сервера не містить коду авторизації");
    }

    if (!this.pendingVerifier) {
      throw new Error("Втрачено verifier для поточної сесії PKCE");
    }

    const tokens = await this.exchangeCodeForTokens(code, this.pendingVerifier);
    this.pendingVerifier = null;
    this.pendingState = null;
    return tokens;
  }

  private async exchangeCodeForTokens(code: string, verifier: string): Promise<TokenResponse> {
    const body = new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: this.redirectUri,
      client_id: this.clientId,
      code_verifier: verifier
    });

    return this.sendTokenRequest(body);
  }

  public async refreshAccessToken(): Promise<TokenResponse> {
    if (!this.refreshToken) {
      throw new Error("Відсутній refresh_token для виконання оновлення");
    }

    // Запобігання гонитві: якщо запит на оновлення вже виконується, повертаємо активний проміс
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const body = new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: this.refreshToken,
      client_id: this.clientId
    });

    this.refreshPromise = this.sendTokenRequest(body).finally(() => {
      this.refreshPromise = null;
    });

    return this.refreshPromise;
  }

  private async sendTokenRequest(body: URLSearchParams): Promise<TokenResponse> {
    const headers: Record<string, string> = {
      "Content-Type": "application/x-www-form-urlencoded",
      "Accept": "application/json"
    };

    if (this.clientSecret) {
      const basic = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString("base64");
      headers["Authorization"] = `Basic ${basic}`;
    }

    const response = await fetch(this.tokenEndpoint, {
      method: "POST",
      headers,
      body: body.toString()
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Помилка запиту токенів [${response.status}]: ${errText}`);
    }

    const tokens = (await response.json()) as TokenResponse;
    this.accessToken = tokens.access_token;
    if (tokens.refresh_token) {
      this.refreshToken = tokens.refresh_token;
    }
    this.expiresAt = Date.now() + (tokens.expires_in ?? 3600) * 1000;
    return tokens;
  }

  public async getValidAccessToken(): Promise<string> {
    const now = Date.now();
    const threshold = this.expiresAt - this.clockSkewSeconds * 1000;

    if (now >= threshold) {
      if (this.refreshToken) {
        await this.refreshAccessToken();
      } else {
        throw new Error("Access token закінчився, а refresh_token відсутній");
      }
    }

    if (!this.accessToken) {
      throw new Error("Клієнт не авторизований");
    }
    return this.accessToken;
  }
}
