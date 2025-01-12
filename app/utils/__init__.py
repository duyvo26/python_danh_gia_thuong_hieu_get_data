import re


def sanitize_for_mysql(input_string):
    # Remove non-ASCII characters (if needed)
    cleaned_string = re.sub(r"[^\x00-\x7F]+", "", input_string)

    # Optionally, you can escape or replace other MySQL problematic characters
    # For example, escape single quotes to prevent SQL injection
    cleaned_string = cleaned_string.replace("'", "''")

    # Return the cleaned string
    return cleaned_string
