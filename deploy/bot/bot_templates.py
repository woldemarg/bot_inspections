from collections import namedtuple

# %%

Menu = namedtuple('Menu', ['add_', 'del_', 'all_', 'cal_'])

main_menu = Menu('Новий код',
                 'Видалити код',
                 'Мої коди',
                 'Перевірки')

# %%

msg_intro = 'Перевірки бізнесу за даними іnspections.gov.ua.\n1. Додайте перший код ЄДРПОУ до свого переліку.\n2. Редагуйте перелік кодів ЄДРПОУ (до {limit}).\n3. Отримайте календар перевірок за кодами у переліку.'
msg_start = 'Оберіть дію:'
msg_enter_code = 'Введіть код:'
msg_enter_done = 'Додати код {code}?'
msg_del_choose = 'Оберіть код:'
msg_del_done = 'Видалити код {code}?'
msg_add_next = 'Збережено код {code}. Оберіть дію:'
msg_code_already_exists = 'Код {code} є у переліку. Оберіть дію:'
msg_del_next = 'Видалено код {code}. Оберіть дію:'
msg_all_codes = 'Перелік кодів:\n{codes}'
msg_no_codes = 'Кодів немає. Оберіть дію:'
msg_calendar_head = '*ЄДРПОУ*: {code}\n*Назва*: {name}\n*Оновлено*: {last_modify}\n*Майбутні перевірки*:'
msg_calendar_date = '\n  _{date}:_'
msg_calendar_info = '\n    ({num}) [деталі...]({url})'
msg_no_inspections = '\n  _відсутні_'
msg_no_data = 'Помилка! За кодом {code} немає даних.'
msg_codes_limit = 'Досягнуто ліміт у {limit} кодів. Будь-ласка, відредагуйте перелік:\n{codes}'
