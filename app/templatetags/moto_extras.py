from django import template
from app.model_map import MODEL_MAP
import re

register = template.Library()

@register.filter
def model_desc(model_id):
    return MODEL_MAP.get(model_id, model_id)

@register.filter
def plate_format(value):
    if not value:
        return ""

    value = value.strip()

    match = re.match(r"([a-zA-Z])(\d+)", value)
    if not match:
        return value.upper()

    letter, numbers = match.groups()

    grouped = " ".join(
        numbers[i:i+3] for i in range(0, len(numbers), 3)
    )

    # ⬇️ CAMBIO AQUÍ
    return f"{letter.upper()}{grouped}"

