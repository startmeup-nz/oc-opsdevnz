# src/oc_opsdevnz/oc_client.py
import hashlib
import json
import os
import time
from typing import Any, Dict, Optional, Literal
import urllib.request, urllib.error

from .secrets import get_oc_token

PROD_URL = "https://api.opencollective.com/graphql/v2"
STAGING_URL = "https://api-staging.opencollective.com/graphql/v2"

def _infer_api_url_from_secret_ref(env_var: str = "OC_SECRET_REF") -> str:
    ref = os.getenv(env_var, "")  # e.g. op://startmeup.nz/api-staging.opencollective.com/credential
    if "api-staging.opencollective.com" in ref:
        return STAGING_URL
    if "api.opencollective.com" in ref:
        return PROD_URL
    return STAGING_URL  # default to staging

# Safer default: staging unless explicitly overridden.
DEFAULT_OC_API_URL = os.getenv("OC_API_URL", STAGING_URL)

AuthMode = Literal["personal", "oauth"]
DEBUG = os.getenv("OC_DEBUG", "").lower() in ("1", "true", "yes")


def _redact(text: str, secrets: Any) -> str:
    """Best-effort redaction to avoid echoing tokens in errors."""
    if not text:
        return text
    for s in secrets or []:
        if s and isinstance(s, str):
            text = text.replace(s, "***REDACTED***")
    return text


def _token_fingerprint(token: Optional[str]) -> str:
    if not token:
        return ""
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return digest[:12]


class OpenCollectiveClient:
    def __init__(
        self,
        api_url: Optional[str] = None,
        token: Optional[str] = None,
        app_name: str = "oc_opsdevnz",
        auth_mode: AuthMode = "personal",
        **kwargs,
    ):
        api_url = api_url or kwargs.pop("base_url", None)
        self.api_url = api_url or DEFAULT_OC_API_URL
        self.token = token or get_oc_token()
        self.app_name = app_name
        self.auth_mode = auth_mode

    @classmethod
    def for_prod(cls, token: Optional[str] = None, app_name: str = "oc_opsdevnz-prod", auth_mode: AuthMode = "personal"):
        return cls(api_url=PROD_URL, token=token, app_name=app_name, auth_mode=auth_mode)

    @classmethod
    def for_staging(cls, token: Optional[str] = None, app_name: str = "oc_opsdevnz-staging", auth_mode: AuthMode = "personal"):
        return cls(api_url=STAGING_URL, token=token, app_name=app_name, auth_mode=auth_mode)

    @classmethod
    def from_secret_ref(cls, secret_ref_env: str = "OC_SECRET_REF", app_name: str = "oc_opsdevnz", auth_mode: AuthMode = "personal"):
        token = get_oc_token(secret_ref_env=secret_ref_env)
        api_url = _infer_api_url_from_secret_ref(secret_ref_env)
        return cls(api_url=api_url, token=token, app_name=app_name, auth_mode=auth_mode)

    def graphql(self, query: str, variables: Optional[Dict[str, Any]] = None, retry: int = 2) -> Dict[str, Any]:
        payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
        req = urllib.request.Request(self.api_url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", self.app_name)

        # Personal token vs OAuth
        if self.auth_mode == "personal":
            req.add_header("Personal-Token", self.token)
        else:
            req.add_header("Authorization", f"Bearer {self.token}")

        last_err = None
        for attempt in range(retry + 1):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    body = resp.read().decode("utf-8")
                    data = json.loads(body)
                    if "errors" in data:
                        raise RuntimeError(f"GraphQL errors: {json.dumps(data['errors'], ensure_ascii=False)}")
                    return data["data"]
            except urllib.error.HTTPError as e:
                # surface server body (helps diagnose 400/401 quickly)
                try:
                    err_body_raw = e.read().decode("utf-8")
                except Exception:
                    err_body_raw = ""

                # Redact secrets from the body; default to omitting 401/403 bodies unless debug is enabled.
                err_body_redacted = _redact(err_body_raw, [self.token])
                body_snippet = ""
                if DEBUG:
                    body_snippet = err_body_redacted[:400]
                else:
                    if e.code in (401, 403):
                        err_body_redacted = ""

                fingerprint = _token_fingerprint(self.token)

                msg = f"HTTP {e.code} {self.api_url} — {e.reason}."
                if DEBUG:
                    msg += f" Body: {body_snippet or '<omitted>'}"
                    if fingerprint:
                        msg += f" Token fingerprint: {fingerprint}"
                else:
                    msg += " Body: <omitted>"

                last_err = RuntimeError(msg)
                if e.code >= 500 and attempt < retry:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                break
            except urllib.error.URLError as e:
                last_err = e
                if attempt < retry:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                break
        raise last_err  # type: ignore

    execute = graphql
