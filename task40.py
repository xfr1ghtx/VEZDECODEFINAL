import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json


def create_response(session, response, **kwargs):
    answer = {'session': session, 'response': response}
    answer['response'].update(kwargs)
    answer['response']['tts'] = answer['response']['text']
    if 'end_session' not in answer['response']:
        answer['response']['end_session'] = False
    answer['response']['tts'] = answer['response']['text']
    answer['version'] = "1.0"
    return answer

users = {}

field_size = 5

mapping = {
    0: '◻',
    1: '◼',
    2: '▨',
    'top': '▲',
    'right': '►',
    'bottom': '▼',
    'left': '◄'
}


def create_user():
    return {
        'snake': [(0, 0)],
        'eat': (5, 7),
        'score': 0,
        'end': False
    }


def draw_snake(snake, eat, action):
    field = [[mapping[0] for _ in range(field_size)] for _ in range(field_size)]
    for node in snake:
        field[node[0]][node[1]] = mapping[1]
    field[eat[0]][eat[1]] = mapping[2]
    field[snake[0][0]][snake[0][1]] = mapping[action]
    return '\n'.join([''.join(row) for row in field])


def get_random_empty_cell(snake):
    cell = random.randint(0, field_size - 1), random.randint(0, field_size - 1)
    while cell in snake:
        cell = random.randint(0, field_size - 1), random.randint(0, field_size - 1)
    return cell


def next_step(game_object, action=None):
    old_snake = game_object['snake']
    new_head = change_head(old_snake[0], action)
    if (new_head[0] not in range(field_size)) or (new_head[1] not in range(field_size)) or (new_head in old_snake):
        game_object['end'] = True
        return
    new_snake = [new_head] + old_snake[:-1]
    if new_head == game_object['eat']:
        game_object['score'] += 1
        new_snake.append(old_snake[-1])
        game_object['eat'] = get_random_empty_cell(new_snake)
    game_object['snake'] = new_snake
    return draw_snake(new_snake, game_object['eat'], action)


def change_head(head, action):
    if action in [0, 'left']:
        return head[0], head[1] - 1
    if action in [0, 'right']:
        return head[0], head[1] + 1
    if action in [0, 'top']:
        return head[0] - 1, head[1]
    if action in [0, 'bottom']:
        return head[0] + 1, head[1]


commands = {
    'start': 'старт, арт, тарт, торт, стар'.split(', '),
    'stop': 'стоп, топ, хватит, прекрати, on_interrupt'.split(', '),
    'left': 'влево, лево, левее, слева, лев'.split(', '),
    'right': 'вправо, право, правее, справа, прав, права, правы'.split(', '),
    'top': 'вверх, верх, выше, верхом'.split(', '),
    'bottom': 'вниз, ниже, низ'.split(', '),
}


def create_button(text):
    return {
        'title': text,
        'payload': {
            'text': text
        }
    }


buttons = [
    create_button('влево'),
    create_button('вправо'),
    create_button('вверх'),
    create_button('вниз')
]

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('proverka'.encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        body = json.loads(body)

        request = body['request']
        session = body['session']

        if request['command'].lower() in commands['start']:
            self.answer_to_start(session)
            return

        if request['command'].lower() in commands['stop']:
            if self.answer_to_stop(session):
                return

        action = [command for command in commands.keys() if request['command'].lower() in commands[command]]
        if len(action) > 0:
            if self.answer_to_move(session, action[0]):
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
        if user_id in users:
            self.send_as_json(create_response(
                session,
                {
                    "text": "Вы уже играете\n" + draw_snake(users[user_id]['snake'], users[user_id]['eat'], 'bottom'),
                },
                buttons=[create_button('Старт')]
            ))
            return
        users[user_id] = create_user()
        users[user_id]['eat'] = get_random_empty_cell([(0, 0)])
        self.send_as_json(create_response(
            session,
            {"text": "Да начнётся великая игра!\n{" + draw_snake(users[user_id]['snake'], users[user_id]['eat'], 'bottom') + "}{}"},
            buttons=buttons
        ))

    def answer_to_stop(self, session):
        user_id = session['user_id']
        if user_id not in users:
            return False

        self.send_as_json(create_response(
            session,
            {
                'text': "Конец\n" + draw_snake(users[user_id]['snake'], users[user_id]['eat'], 'bottom'),
                "end_session": True
            },
            buttons=[create_button('Старт')]
        ))
        del (users[user_id])
        return True

    def answer_to_move(self, session, action):
        user_id = session['user_id']
        if user_id not in users:
            return False

        new_step = next_step(users[user_id], action)
        if users[user_id]['end']:
            self.send_as_json(create_response(
                session,
                {"text": f"Вы проиграли( \nВаш счёт: {users[user_id]['score']}\n"
                         f"{draw_snake(users[user_id]['snake'], users[user_id]['eat'], 'bottom')}"},
                buttons=[create_button('Старт')]
            ))
            del(users[user_id])
            return True
        self.send_as_json(create_response(
            session,
            {"text": new_step},
            buttons=buttons
        ))
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
print(443)
httpd.serve_forever()
