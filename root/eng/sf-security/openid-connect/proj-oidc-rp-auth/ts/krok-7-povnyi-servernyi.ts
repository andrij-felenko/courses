import express, { Request, Response } from 'express';
import cookieParser from 'cookie-parser';
import crypto from 'crypto';

const app = express();
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));

const CLIENT_ID = 'my-saas-client-id';
const CLIENT_SECRET = 'super-secret-key-123';
const ISSUER = 'https://accounts.example.com';
const REDIRECT_URI = 'https://my-app.com/auth/callback';

const pendingStates = new Map<string, { nonce: string; codeVerifier: string; createdAt: number }>();
const userSessions = new Map<string, { sub: string; email: string; name: string; idToken: string }>();

const jwksMgr = new JwksManager(`${ISSUER}/.well-known/jwks.json`);

app.get('/auth/login', (req: Request, res: Response) => {
  const ctx = createAuthorizationUrl(`${ISSUER}/authorize`, CLIENT_ID, REDIRECT_URI);
  pendingStates.set(ctx.state, {
    nonce: ctx.nonce,
    codeVerifier: ctx.codeVerifier,
    createdAt: Date.now(),
  });
  res.redirect(ctx.authUrl);
});

app.get('/auth/callback', async (req: Request, res: Response) => {
  const state = req.query.state as string;
  const code = req.query.code as string;
  const error = req.query.error as string;

  if (error) {
    return res.status(400).send(`Помилка провайдера: ${error}`);
  }

  if (!state || !pendingStates.has(state)) {
    return res.status(403).send('Недійсний або відсутній state');
  }

  const savedCtx = pendingStates.get(state)!;
  pendingStates.delete(state);

  try {
    const tokenRes = await exchangeCodeForTokens(
      `${ISSUER}/token`,
      CLIENT_ID,
      CLIENT_SECRET,
      code,
      savedCtx.codeVerifier,
      REDIRECT_URI
    );

    const claims = await validateIdToken(
      tokenRes.id_token,
      ISSUER,
      CLIENT_ID,
      savedCtx.nonce,
      jwksMgr,
      tokenRes.access_token
    );

    let profile: Record<string, any> = {};
    if (tokenRes.access_token) {
      profile = await fetchUserInfo(`${ISSUER}/userinfo`, tokenRes.access_token);
    }

    const sessionId = crypto.randomBytes(32).toString('base64url');
    userSessions.set(sessionId, {
      sub: claims.sub,
      email: profile.email || claims.email || '',
      name: profile.name || claims.name || '',
      idToken: tokenRes.id_token,
    });

    res.cookie('session_id', sessionId, {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      path: '/',
    });
    res.redirect('/dashboard');
  } catch (err: any) {
    res.status(401).send(`Помилка валідації OIDC: ${err.message}`);
  }
});
