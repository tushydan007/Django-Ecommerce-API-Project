from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_size_kb = 2000
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"Uploaded file cannot be larger than {max_size_kb}kb")
