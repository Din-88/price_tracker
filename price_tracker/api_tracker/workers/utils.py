from django.db.models import Value, CharField, Aggregate


class GroupConcat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s%(expressions)s)'

    def __init__(self, expression, distinct=False, **extra):
        super().__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            output_field=CharField(),
            **extra,
        )


def get_plural_word(n, words):
    # Определяем остаток от деления на 10
    remainder = n % 10
    # Определяем остаток от деления на 100
    remainder100 = n % 100
    # Если остаток от деления на 100 от 11 до 19, то используем третье слово во множественном числе
    if 11 <= remainder100 <= 19:
        return words[2]
    # Если остаток от деления на 10 равен 1, то используем первое слово во множественном числе
    elif remainder == 1:
        return words[0]
    # Если остаток от деления на 10 от 2 до 4, то используем второе слово во множественном числе
    elif 2 <= remainder <= 4:
        return words[1]
    # Во всех остальных случаях используем третье слово во множественном числе
    else:
        return words[2]


def message_updated_trackers(notify_cases, total):
    msg = f'У Вас {total} ' \
        f'{get_plural_word(total, ["обновленный", "обновленныx", "обновленныx"])} ' \
        f'{get_plural_word(total, ["Трекер", "Трекера", "Трекеров"])}.\r\n'
    
    messages = [msg]
    for notify in notify_cases:
        temp_msg = f'{notify["count"]} ' \
            f'{get_plural_word(notify["count"], ["Трекер", "Трекера", "Трекеров"])}'
        if notify['need_notify_case'] == '>':
            message = f"Цена на {temp_msg} повысилась.\r\n"
        elif notify['need_notify_case'] == '<':
            message = f"Цена на {temp_msg} понизилась.\r\n"
        else:
            message = ''
        messages.append(message)
    return ''.join(messages)