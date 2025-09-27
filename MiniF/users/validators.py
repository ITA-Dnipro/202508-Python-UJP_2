import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Пароль повинен містити хоча б одну велику літеру."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Ваш пароль повинен містити хоча б одну велику літеру.")

