import urllib
import math
import json
import requests
from datetime import datetime
import numpy as np
import bot_templates
from bot_dbhelper import DBHelper


# %%

class ControlBot(DBHelper):
    def __init__(self,
                 BOT_URL,
                 CODES_LIMIT,
                 INS_URL
                 ):
        DBHelper.__init__(self)
        self.BOT_URL = BOT_URL
        self.CODES_LIMIT = CODES_LIMIT
        self.INS_URL = INS_URL
        self.buttons_menu = self.build_custom_keyboard(bot_templates.main_menu)
        self.buttons_confirm = self.build_confirm_keyboard()
        self.buttons_digit = self.build_digit_keyboard()
        self.inline_inputs = {}

    @staticmethod
    def to_date(st, fr='%d-%m-%Y'):
        return datetime.strptime(st, fr)

    @staticmethod
    def get_url(url):
        response = requests.get(url)
        content = response.content.decode('utf8')
        return content

    @staticmethod
    def build_confirm_keyboard():
        keyboard = [[{'text': 'Так', 'callback_data': 'yes'},
                     {'text': 'Ні', 'callback_data': 'no'}]]
        reply_markup = {'inline_keyboard': keyboard}
        return json.dumps(reply_markup)

    @staticmethod
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

    @staticmethod
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

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def send_message(self,
                     m_text,
                     chat_id,
                     reply_markup=None,
                     markdown=None):
        m_text = urllib.parse.quote_plus(m_text)
        url = (self.BOT_URL + 'sendMessage?text={}&chat_id={}'
               .format(m_text, chat_id))
        if reply_markup:
            url += '&reply_markup={}'.format(reply_markup)
        if markdown:
            url += '&parse_mode=Markdown'
        self.get_url(url)

    def get_inspections(self, id_code):
        url = self.INS_URL + '&code={}'.format(id_code)
        response = self.get_json_from_url(url)
        if response['status'] == 'error':
            return None
        inspections = {}
        items = [x.get('parts', None) for x
                 in response['items'] if x.get('parts', None)]
        if not items:
            return None
        items_flat = [item for sublist in items for item in sublist]
        last_modify = max([self.to_date(x['last_modify'].split()[0])
                           for x in items_flat])
        name, address = (
            [(x['name'], x['address']) for x in items_flat
             if self.to_date(x['last_modify'].split()[0]) == last_modify][0]
        )
        # TODO dict.get(key, None)
        calendar = [[self.to_date(x['date_start'].split()[0], '%Y-%m-%d'),
                     x['activity_type'].lower(),
                     x['link']]
                    for x in items_flat]
        inspections['name'] = name
        inspections['address'] = address
        inspections['calendar'] = calendar
        inspections['last_modify'] = last_modify
        return inspections

    def make_calendar_message(self, id_code):
        inspections = self.get_inspections(id_code)
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

    def handle_updates(self, update):
        try:
            callback_query = update.get('callback_query', None)
            if callback_query:
                chat = callback_query['message']['chat']['id']
                if chat not in self.inline_inputs:
                    self.inline_inputs[chat] = []
                input_data = callback_query['data']
                if input_data == 'OK':
                    code = ''.join(str(x) for x in self.inline_inputs[chat])
                    codes = self.get_codes(chat)
                    if code not in codes:
                        self.send_message((bot_templates.msg_enter_done
                                           .format(code=code)),
                                          chat,
                                          self.buttons_confirm)
                    else:
                        self.send_message(
                            (bot_templates.msg_code_already_exists
                             .format(code=code)),
                            chat,
                            self.buttons_menu
                        )
                elif input_data == '<':
                    if self.inline_inputs[chat]:
                        self.inline_inputs[chat].pop()
                    else:
                        pass
                elif input_data == 'yes':
                    code = ''.join(str(x) for x in self.inline_inputs[chat])
                    codes = self.get_codes(chat)
                    if code in codes:
                        self.del_code(chat, code)
                        self.send_message((bot_templates.msg_del_next
                                           .format(code=code)),
                                          chat,
                                          self.buttons_menu)
                    else:
                        self.add_code(chat, code)
                        self.send_message((bot_templates.msg_add_next
                                           .format(code=code)),
                                          chat,
                                          self.buttons_menu)
                    self.inline_inputs.pop(chat, None)
                elif input_data == 'no':
                    self.inline_inputs.pop(chat, None)
                    self.send_message(bot_templates.msg_start,
                                      chat,
                                      self.buttons_menu)
                else:
                    self.inline_inputs[chat].append(input_data)
            else:
                chat = update['message']['chat']['id']
                text = update['message']['text']
                codes = self.get_codes(chat)
                self.inline_inputs.pop(chat, None)
                if text == '/start':
                    self.send_message((bot_templates.msg_intro
                                       .format(limit=self.CODES_LIMIT)),
                                      chat,
                                      self.buttons_menu)
                elif text == bot_templates.main_menu.add_:
                    if len(codes) == self.CODES_LIMIT:
                        codes_list = '\n'.join(codes)
                        self.send_message(
                            (bot_templates.msg_codes_limit
                             .format(limit=self.CODES_LIMIT,
                                     codes=codes_list)),
                            chat,
                            self.buttons_menu
                        )
                    else:
                        self.send_message(bot_templates.msg_enter_code,
                                          chat,
                                          self.buttons_digit)
                elif text == bot_templates.main_menu.del_:
                    if len(codes) > 0:
                        buttons_codes = self.build_custom_keyboard(codes)
                        self.send_message(bot_templates.msg_del_choose,
                                          chat,
                                          buttons_codes)
                    else:
                        self.send_message(bot_templates.msg_no_codes,
                                          chat,
                                          self.buttons_menu)
                elif text in codes:
                    if chat not in self.inline_inputs:
                        self.inline_inputs[chat] = []
                    self.inline_inputs[chat].append(text)
                    self.send_message((bot_templates.msg_del_done
                                       .format(code=text)),
                                      chat,
                                      self.buttons_confirm)
                elif text == bot_templates.main_menu.all_:
                    if len(codes) > 0:
                        codes_list = '\n'.join(codes)
                        self.send_message((bot_templates.msg_all_codes
                                           .format(codes=codes_list)),
                                          chat,
                                          self.buttons_menu)
                    else:
                        self.send_message(bot_templates.msg_no_codes,
                                          chat,
                                          self.buttons_menu)
                elif text == bot_templates.main_menu.cal_:
                    if len(codes) > 0:
                        for code in codes:
                            message = self.make_calendar_message(code)
                            self.send_message(message,
                                              chat,
                                              self.buttons_menu,
                                              markdown=True)
                    else:
                        self.send_message(bot_templates.msg_no_codes,
                                          chat,
                                          self.buttons_menu)
                else:
                    self.send_message(bot_templates.msg_start,
                                      chat,
                                      self.buttons_menu)
        except KeyError:
            pass
