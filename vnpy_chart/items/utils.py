def format_decimal(number, decimal_places=2):
    formatted_number = f'{number:.{decimal_places}f}'
    if formatted_number.endswith('0' * decimal_places):
        return str(int(number))
    return formatted_number
