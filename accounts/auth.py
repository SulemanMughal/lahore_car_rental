# accounts/auth.py
from rest_framework_simplejwt.tokens import RefreshToken

ROLE_TO_SCOPES = {
    "customer": {"car:read", "booking:read", "booking:create"},
    "fleet_manager": {"car:read", "car:write", "doc:verify", "booking:read"},
    "support": {"booking:read", "booking:write"},
    "finance": {"payment:read", "payment:write"},
    "admin": {"*"},
}

def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["scp"] = " ".join(sorted(ROLE_TO_SCOPES.get(user.role, set())))
    refresh["ver"] = user.token_version  # optional: token-versioning for revocation
    return {"access": str(refresh.access_token), "refresh": str(refresh)}
