from op_opsdevnz.onepassword import SecretError, get_secret

def get_oc_token() -> str:
    """Resolve the OpenCollective token via 1Password (human CLI for local dev)."""
    try:
        return get_secret(
            secret_ref_env="OC_SECRET_REF",  # op://... reference you exported
            env_override="OC_TOKEN",          # optional local override
            prefer_cli=True                   # force CLI for local dev
        )
    except SecretError as e:
        raise RuntimeError(f"Failed to resolve OC token: {e}") from e
