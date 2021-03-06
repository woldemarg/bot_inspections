import os
from fastapi import FastAPI, Request
import uvicorn
import urllib
from datetime import datetime
import math
import json
import requests
import numpy as np
import bot_config
import bot_templates
from bot_dbhelper import DBHelper

# %%

db = DBHelper()


# %%

def send_message(m_text,
                 chat_id,
                 reply_markup=None,
                 markdown=None):
    m_text = urllib.parse.quote_plus(m_text)
    url = (bot_config.BOT_URL + 'sendMessage?text={}&chat_id={}'
           .format(m_text, chat_id))
    if reply_markup:
        url += '&reply_markup={}'.format(reply_markup)
    if markdown:
        url += '&parse_mode=Markdown'
    get_url(url)


# %%

def build_custom_keyboard(items, n_cols=2, n_rows=None):
    if not n_rows:
        n_rows = int(math.ceil(len(items) / n_cols))
    else:
        n_cols = int(math.ceil(len(items) / n_rows))
    full_arr = np.full((n_rows, n_cols), '', dtype='<U12')
    full_arr.flat[: len(items)] = items
    keyboard = full_arr.tolist()
    reply_markup = {'keyboard': keyboard,
                    'one_time_keyboard': True,
                    'resize_keyboard': True}
    return json.dumps(reply_markup)


# %%

def build_digit_keyboard():
    keyboard = [[{'text': '1', 'callback_data': '1'},
                 {'text': '2', 'callback_data': '2'},
                 {'text': '3', 'callback_data': '3'}],
                [{'text': '4', 'callback_data': '4'},
                 {'text': '5', 'callback_data': '5'},
                 {'text': '6', 'callback_data': '6'}],
                [{'text': '7', 'callback_data': '7'},
                 {'text': '8', 'callback_data': '8'},
                 {'text': '9', 'callback_data': '9'}],
                [{'text': '<', 'callback_data': '<'},
                 {'text': '0', 'callback_data': '0'},
                 {'text': 'OK', 'callback_data': 'OK'}]]
    reply_markup = {'inline_keyboard': keyboard}
    return json.dumps(reply_markup)


# %%

def build_confirm_keyboard():
    keyboard = [[{'text': 'Так', 'callback_data': 'yes'},
                 {'text': 'Ні', 'callback_data': 'no'}]]
    reply_markup = {'inline_keyboard': keyboard}
    return json.dumps(reply_markup)


# %%

def to_date(st, fr='%d-%m-%Y'):
    return datetime.strptime(st, fr)


# %%

def get_url(url):
    response = requests.get(url)
    content = response.content.decode('utf8')
    return content


# %%

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


# %%

def get_inspections(id_code):
    url = bot_config.INS_URL + '&code={}'.format(id_code)
    response = get_json_from_url(url)
    if response['status'] == 'error':
        return None
    inspections = {}
    items = [x.get('parts', None) for x
             in response['items'] if x.get('parts', None)]
    if not items:
        return None
    items_flat = [item for sublist in items for item in sublist]
    last_modify = max([to_date(x['last_modify'].split()[0])
                       for x in items_flat])
    name, address = [(x['name'], x['address']) for x in items_flat
                     if to_date(x['last_modify'].split()[0]) == last_modify][0]
    # TODO check if key does not exist
    calendar = [[to_date(x['date_start'].split()[0], '%Y-%m-%d'),
                 x['activity_type'].lower(),
                 x['link']]
                for x in items_flat]
    inspections['name'] = name
    inspections['address'] = address
    inspections['calendar'] = calendar
    inspections['last_modify'] = last_modify
    return inspections


# %%

def make_calendar_message(id_code):
    inspections = get_inspections(id_code)
    if inspections:
        calendar = []
        calendar.append(bot_templates.msg_calendar_head
                        .format(code=id_code,
                                name=inspections['name'],
                                last_modify=datetime
                                .strftime(inspections['last_modify'],
                                          '%Y-%m-%d')))
        active_list = [(x[0], x[-1]) for x in inspections['calendar']
                       if x[0] > datetime.now()]
        if not active_list:
            calendar.append(bot_templates.msg_no_inspections)
        active_dict = {}
        for item in active_list:
            key, value = item
            key = datetime.strftime(key, '%Y-%m-%d')
            if key not in active_dict:
                active_dict[key] = [value]
            else:
                active_dict[key].append(value)

        sorted_dict = dict(sorted(active_dict.items()))

        for key, value in sorted_dict.items():
            calendar.append(bot_templates.msg_calendar_date
                            .format(date=key))
            for i, u in enumerate(value, 1):
                calendar.append(bot_templates.msg_calendar_info
                                .format(num=i, url=u))
        return ''.join(calendar)
    return bot_templates.msg_no_data.format(code=id_code)


# %%

def handle_updates(update):
    try:
        callback_query = update.get('callback_query', None)
        if callback_query:
            chat = callback_query['message']['chat']['id']
            if chat not in inline_inputs:
                inline_inputs[chat] = []
            input_data = callback_query['data']
            if input_data == 'OK':
                code = ''.join(str(x) for x in inline_inputs[chat])
                codes = db.get_codes(chat)
                if code not in codes:
                    send_message((bot_templates.msg_enter_done
                                  .format(code=code)),
                                 chat,
                                 buttons_confirm)
                else:
                    send_message((bot_templates.msg_code_already_exists
                                  .format(code=code)),
                                 chat,
                                 buttons_menu)
            elif input_data == '<':
                if inline_inputs[chat]:
                    inline_inputs[chat].pop()
                else:
                    pass
            elif input_data == 'yes':
                code = ''.join(str(x) for x in inline_inputs[chat])
                codes = db.get_codes(chat)
                if code in codes:
                    db.del_code(chat, code)
                    send_message((bot_templates.msg_del_next
                                  .format(code=code)),
                                 chat,
                                 buttons_menu)
                else:
                    db.add_code(chat, code)
                    send_message((bot_templates.msg_add_next
                                  .format(code=code)),
                                 chat,
                                 buttons_menu)
                inline_inputs.pop(chat, None)
            elif input_data == 'no':
                inline_inputs.pop(chat, None)
                send_message(bot_templates.msg_start,
                             chat,
                             buttons_menu)
            else:
                inline_inputs[chat].append(input_data)
        else:
            chat = update['message']['chat']['id']
            text = update['message']['text']
            codes = db.get_codes(chat)
            inline_inputs.pop(chat, None)
            if text == '/start':
                send_message((bot_templates.msg_intro
                              .format(limit=bot_config.CODES_LIMIT)),
                             chat,
                             buttons_menu)
            elif text == bot_templates.main_menu.add_:
                if len(codes) == bot_config.CODES_LIMIT:
                    codes_list = '\n'.join(codes)
                    send_message((bot_templates.msg_codes_limit
                                  .format(limit=bot_config.CODES_LIMIT,
                                          codes=codes_list)),
                                 chat,
                                 buttons_menu)
                else:
                    send_message(bot_templates.msg_enter_code,
                                 chat,
                                 buttons_digit)
            elif text == bot_templates.main_menu.del_:
                if len(codes) > 0:
                    buttons_codes = build_custom_keyboard(codes)
                    send_message(bot_templates.msg_del_choose,
                                 chat,
                                 buttons_codes)
                else:
                    send_message(bot_templates.msg_no_codes,
                                 chat,
                                 buttons_menu)
            elif text in codes:
                if chat not in inline_inputs:
                    inline_inputs[chat] = []
                inline_inputs[chat].append(text)
                send_message((bot_templates.msg_del_done
                              .format(code=text)),
                             chat,
                             buttons_confirm)
            elif text == bot_templates.main_menu.all_:
                if len(codes) > 0:
                    codes_list = '\n'.join(codes)
                    send_message((bot_templates.msg_all_codes
                                  .format(codes=codes_list)),
                                 chat,
                                 buttons_menu)
                else:
                    send_message(bot_templates.msg_no_codes,
                                 chat,
                                 buttons_menu)
            elif text == bot_templates.main_menu.cal_:
                if len(codes) > 0:
                    for code in codes:
                        message = make_calendar_message(code)
                        send_message(message,
                                     chat,
                                     buttons_menu,
                                     markdown=True)
                else:
                    send_message(bot_templates.msg_no_codes,
                                 chat,
                                 buttons_menu)
            else:
                send_message(bot_templates.msg_start,
                             chat,
                             buttons_menu)
    except KeyError:
        pass


# %%

app = FastAPI()

# %%

db.setup()
inline_inputs = {}
buttons_menu = build_custom_keyboard(bot_templates.main_menu)
buttons_confirm = build_confirm_keyboard()
buttons_digit = build_digit_keyboard()


# %%

@app.post('/')
async def webhook(request: Request):
    data = await request.json()
    handle_updates(data)
    return {'result': 'OK'}

# %%

PORT = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    uvicorn.run('bot_webhook:app', host='127.0.0.1', port=PORT)
