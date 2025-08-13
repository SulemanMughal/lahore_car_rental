# core/permissions.py
from rest_framework.permissions import BasePermission

def _claims(request):
    tok = getattr(request, "auth", None)
    # SimpleJWT returns a token (mapping-like). Prefer .payload if present.
    return getattr(tok, "payload", tok) or {}

class HasAnyRole(BasePermission):
    ALLOWED = {"admin"}  # override per view

    def has_permission(self, request, view):
        claims = _claims(request)
        role = (claims.get("role") or "").lower()
        return role in self.ALLOWED or "*" in (claims.get("scp") or "")

class HasScope(BasePermission):
    REQUIRED = {"car:write"}  # override per view

    def has_permission(self, request, view):
        claims = _claims(request)
        scopes = set((claims.get("scp") or "").split())
        return "*" in scopes or bool(self.REQUIRED & scopes)
