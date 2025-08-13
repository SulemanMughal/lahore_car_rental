# rental/validators.py
import re, datetime
from django.utils import timezone
from rest_framework import serializers

_PLATE_RE = re.compile(r"^[A-Z0-9-]{3,16}$", re.I)

def validate_tz_aware(dt, field="datetime"):
    if timezone.is_naive(dt):
        raise serializers.ValidationError({field: "must be timezone-aware (ISO8601 with offset)."})
    return dt

def validate_start_end(start, end):
    validate_tz_aware(start, "start")
    validate_tz_aware(end, "end")
    if start >= end:
        raise serializers.ValidationError("start must be before end.")
    return start, end

def validate_year(year, min_year=1970):
    this_year = datetime.date.today().year
    if not (min_year <= year <= this_year + 1):
        raise serializers.ValidationError(f"Year must be between {min_year} and {this_year+1}.")
    return year

def validate_plate(plate: str):
    p = (plate or "").strip().upper()
    if not _PLATE_RE.match(p):
        raise serializers.ValidationError("Plate must be alphanumeric/dash, 3–16 chars.")
    return p
