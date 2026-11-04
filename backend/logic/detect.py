"""Find where a person gets stuck on a task.

Placeholder: always returns "none" until the real rules are built.
"""


def detect(events, definitions, days_since_last, task=None):
    """Return a list of sticking points, for example:
    [{"code": "stuck_at_step", "step_id": "s5", "evidence": "paused 3 min at s5"}]
    """
    return [{"code": "none", "step_id": None, "evidence": ""}]