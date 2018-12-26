import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy


def validate_organization_number(organization_number: int):
    organization_number_str = str(organization_number)
    match = re.match('^(16)?([1-9]{2}[2-9][0-9]{7})$', organization_number_str)
    if not match:
        raise ValidationError(
            gettext_lazy('%(organization_number)s is invalid'),
            params={'organization_number': organization_number}
        )
    _validate_checksum_digit(match.group(2), organization_number)


def _validate_checksum_digit(ten_digit_organization_number: str, organization_number: int):
    digits = [int(d) for d in re.sub(r'\D', '', ten_digit_organization_number)][-10:]
    even_digit_sum = sum(x if x < 5 else x - 9 for x in digits[::2])
    if not sum(digits, even_digit_sum) % 10 == 0:
        raise ValidationError(
            gettext_lazy('%(organization_number)s is invalid'),
            params={'organization_number': organization_number}
        )
