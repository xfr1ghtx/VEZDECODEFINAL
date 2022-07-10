import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json


def create_question(text, answers, category):
    return {
        'text': text,
        'answers': answers,
        'category': category
    }


def create_card(pic_id, card_type="BigImage", url=None):
    return {
        'type': card_type,
        'image_id': pic_id,
        'url': url
    }


cards = {
    'backend': create_card(457239019),
    'mobile': create_card(457239018),
    'security': create_card(457239020),
    'algorithms': create_card(457239017),
    'mem': create_card(457239022, "MiniApp", "https://vk.com/app7543093")
}

def create_counter():
    return {
        'backend': 0,
        'security': 0,
        'mobile': 0,
        'algorithms': 0,
        'stage': 0
    }


def create_response(session, response, **kwargs):
    answer = {'session': session, 'response': response}
    answer['response'].update(kwargs)
    answer['version'] = "1.0"
    return answer



questions = [
    create_question("<speaker audio_vk_id=2000512046_456239028>{Что выведет программа?}{} \n<speak>let a = 5 let b = 7 console.log({a+b}{ а плюс ^бэ^ })</speak> <s>Введите текст</s>",
        ["12"], 'algorithms'),
    create_question("На каком языке пишут приложения для IOS?",
        ["swift", "свифт", "обжектив-си", "objective-c"], 'mobile'),
    create_question("<speaker audio_vk_id=2000512046_456239026>{Как называется самый распространённый язык для работы с реляционными базами данных}{}",
        ["sql"], 'backend'),
    create_question("<speaker audio_vk_id=2000512046_456239027>{Как называется вид инъекции, направленный на взлом реляцонных баз данных?}{} Введите текст",
        ["sql", "sql-injection", "sql-инъекция"], 'security'),
    create_question("Интерфейс для взаимодействия других программ с вашим сервисом",
        ["api", "апи"], 'backend'),
    create_question("Заполните многоточие, чтобы выдать всем пользователям все права для этого файла: \nsudo chmod " +
        "<...> /vezdekod/vezdehits.txt?",
        ["777"], 'security'),
    create_question("Какую сред`у разработки используют для создания android-приложений?",
        ["android studio, androidstudio"], 'mobile'),
    create_question("Как`ой `алгоритм имеет в ^худшем^ случае асимпт`отитическую сложность {nlogn}{эн лог эн}?" +
        "\n1. quickSort(X)\n2. bubbleSort(X)\n3. mergeSort(X)",
        ["3"], 'algorithms')
]
users = {}

commands = {
    'start': ['старт'],
    'eat': ["съем"],
    'break': ["выброшу"],
    'stop': ["on_interrupt"]
}

def create_button(text):
    return {
        'title': text,
        'payload': {
            'text': text
        }
    }


meals = ['яблоком', 'груздём', 'молоком', 'икрой']
no_meals = ['шкафом', 'кошкой', 'потолком', 'бездной']


def generate_new():
    is_meal = bool(random.randint(0, 1))
    item = meals[random.randint(0, len(meals) - 1)] if is_meal else no_meals[random.randint(0, len(no_meals) - 1)]
    return is_meal, item


buttons = [
    create_button('съем'),
    create_button('выброшу'),
    create_button('стоп')
]


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('proverka'.encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        body = json.loads(body)

        request = body['request']
        session = body['session']

        if request['command'].lower() in commands['start']:
            self.answer_to_start(session)
            return

        if request['command'].lower() in commands['eat']:
            if self.answer_to_eat(session):
                return

        if request['command'].lower() in commands['break']:
            if self.answer_to_break(session):
                return

        if request['command'].lower() in commands['stop']:
            if self.answer_to_stop(session):
                return

        self.send_as_json(create_response(
            session,
            {
                "text": "Не понял.\nЧтобы начать игру, скажите Старт",
                "tts": "Не понял.\nЧтобы начать игру, скажите Старт",
                "end_session": False
            },
            buttons=[create_button('Старт')]
        ))

    def answer_to_start(self, session):
        user_id = session['user_id']
        is_meal, item = generate_new()

        users[user_id] = {
            'seria': 0,
            'is_meal': is_meal
        }
        self.send_as_json(create_response(
            session,
            {
                'text': f"Да начнётся великая игра! \n Что вы сделаете с {item}?",
                'tts': f"Да начнётся великая игра! \n Что вы сделаете с {item}?",
                "end_session": False
            },
            buttons=buttons
        ))

    def answer_to_eat(self, session):
        user_id = session['user_id']
        if user_id not in users:
            return False
        if users[user_id]['is_meal']:
            users[user_id]['seria'] += 1
        else:
            users[user_id]['seria'] = 0
        is_meal, item = generate_new()
        users[user_id]['is_meal'] = is_meal
        blocks = ''.join(["▓" for i in range(users[user_id]['seria'])])
        self.send_as_json(create_response(
            session,
            {
                'text': "{" + f"{blocks} {users[user_id]['seria']}" + "}{" + f"Серия побед: {users[user_id]['seria']}" + "}" + f"\n А что вы сделаете с {item}?",
                'tts': f"Серия побед: {users[user_id]['seria']} \n А что вы сделаете с {item}?",
                "end_session": False
            },
            buttons=buttons
        ))
        return True

    def answer_to_break(self, session):
        user_id = session['user_id']
        if user_id not in users:
            return False

        users[user_id]['is_meal'] = (not users[user_id]['is_meal'])
        return self.answer_to_eat(session)

    def answer_to_stop(self, session):
        user_id = session['user_id']
        if user_id not in users:
            return False

        blocks = ''.join(["▓" for i in range(users[user_id]['seria'])])
        self.send_as_json(create_response(
            session,
            {
                'text': "{" + blocks + "}{" + f"Серия побед: {users[user_id]['seria']}" + "}" + f"\n Поздравляем! Отличный результат!",
                'tts': "{" + blocks + "}{" + f"Серия побед: {users[user_id]['seria']}" + "}" + f"\n Поздравляем! Отличный результат!",
                "end_session": True
            },
            buttons=[create_button('Старт')]
        ))
        del(users[user_id])
        return True

    def send_as_json(self, answer):
        self.wfile.write(bytes(json.dumps(answer), "utf-8"))


server_address = ('0.0.0.0', 443)
httpd = HTTPServer(server_address, MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               keyfile='/etc/letsencrypt/live/vezdedomen.mooo.com/privkey.pem',
                               certfile='/etc/letsencrypt/live/vezdedomen.mooo.com/fullchain.pem',
                               ssl_version=ssl.PROTOCOL_TLS)
print(server_address)
httpd.serve_forever()
