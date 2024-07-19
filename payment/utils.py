from typing import Self


def check_required_fields(form, required_fields: list[str]):
    """
    Check if required fields are present in the form data.
    """
    for field in required_fields:
        if not form.cleaned_data.get(field):
            form.add_error(
                field, f"{field.replace('_', ' ').capitalize()} is required."
            )
