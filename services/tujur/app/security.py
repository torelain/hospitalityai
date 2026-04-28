from fastapi import Header, HTTPException, Request


async def require_cron_token(
    request: Request,
    x_cron_token: str | None = Header(default=None, alias="X-Cron-Token"),
) -> None:
    """Fail-closed shared-secret check for cron endpoints.

    Returns 503 when no token is configured (so the route can't accidentally
    serve traffic without auth) and 401 on a mismatch."""
    expected = request.app.state.cron_token
    if not expected:
        raise HTTPException(status_code=503, detail="cron auth not configured")
    if x_cron_token != expected:
        raise HTTPException(status_code=401, detail="invalid cron token")
