from django import template

register = template.Library()

def plural_ru(value, forms):
    # forms: ('год', 'года', 'лет')
    n = abs(int(value))
    if 11 <= (n % 100) <= 14:
        return forms[2]
    if n % 10 == 1:
        return forms[0]
    if 2 <= n % 10 <= 4:
        return forms[1]
    return forms[2]

@register.filter
def years_ru(value):
    return plural_ru(value, ('год', 'года', 'лет'))

@register.filter
def months_ru(value):
    return plural_ru(value, ('месяц', 'месяца', 'месяцев')) 