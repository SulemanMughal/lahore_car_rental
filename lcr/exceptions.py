# core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from django.utils.translation import gettext_lazy as _
import traceback

def custom_exception_handler(exc, context):
    print(traceback.format_exc())
    resp = exception_handler(exc, context)
    request = context.get("request")
    trace_id = getattr(request, "request_id", None)

    if resp is None:
        # Unhandled -> 500 envelope
        return _wrap(500, False, None, {"code": "server_error", "message": "Internal server error"}, trace_id)

    # DRF already set status_code & data; normalize into our envelope
    detail = resp.data
    error = {"code": "error", "message": _("Request failed"), "details": detail}

    # Specifics
    if resp.status_code == 400:
        error["code"] = "bad_request"
        error["message"] = _("Validation error")
    elif resp.status_code in (401, 403):
        error["code"] = "unauthorized" if resp.status_code == 401 else "forbidden"
    elif resp.status_code == 404:
        error["code"] = "not_found"
    elif resp.status_code == 429 or isinstance(exc, Throttled):
        error["code"] = "rate_limited"
        error["message"] = _("Too many requests. Try later.")
        if isinstance(exc, Throttled):
            error["details"] = {"wait": exc.wait}

    return _wrap(resp.status_code, False, None, error, trace_id)

def _wrap(status_code, success, data, error, trace_id):
    from rest_framework.response import Response
    body = {"success": success, "data": data, "error": error, "trace_id": trace_id}
    return Response(body, status=status_code)
