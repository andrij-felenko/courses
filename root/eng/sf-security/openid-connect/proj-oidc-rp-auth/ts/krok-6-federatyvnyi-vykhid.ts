export function createLogoutUrl(
  endSessionEndpoint: string,
  idTokenHint: string,
  postLogoutRedirectUri: string,
  state?: string
): string {
  const url = new URL(endSessionEndpoint);
  url.searchParams.set('id_token_hint', idTokenHint);
  url.searchParams.set('post_logout_redirect_uri', postLogoutRedirectUri);
  if (state) {
    url.searchParams.set('state', state);
  }
  return url.toString();
}
