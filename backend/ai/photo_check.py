"""Photo safety check (Role D, spec item D7).

The Build Spec names this file. The code lives in high_risk.py, so both names work.
The prompt is backend/prompts/photo_check_system.md.

  microwave_safe(image)  "is this microwave safe": only a quoted label can say yes, 3 of 3 asks must agree
  cook_time(image)       "how long do I heat it": only a time printed on the package, 3 of 3 must match
"""
from .high_risk import (  # noqa: F401
    ASKS,
    COOK_TIME_HANDOFF_REPLY,
    UNSAFE_REPLY,
    cook_time,
    microwave_safe,
)
