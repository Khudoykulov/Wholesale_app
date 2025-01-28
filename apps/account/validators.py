import re
from django.core.validators import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    uzbek_regex = r'^99?\d{9}$'
    validate = re.match(uzbek_regex, value)
    if not validate:
        raise ValidationError(_('Invalid phone number format! Phone number must be korea number ! xx xxx xxx xxx'))
