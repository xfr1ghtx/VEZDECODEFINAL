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

field_size = 8

mapping = {
    0: '◻',
    1: '◼',
    2: '▨'
}


def draw_figure(figure):
    return '\n'.join([''.join([mapping[elem] for elem in line]) for line in figure])


def create_user():
    return {
        'field': [[0 for _ in range(field_size)] for _ in range(field_size)],
        'figure': None,
        'score': 0
    }


def left_rotate(figure):
    size = len(figure)
    return [[figure[size - j - 1][i] for j in range(size)] for i in range(size)]


def left_rotate_in_matrix(matrix, top, left, size):
    result = []
    for i in range(len(matrix)):
        result.append([])
        for j in range(len(matrix)):
            result[i].append(matrix[size - 1 - (j - left) + top][i - top + left] if (
                    (j in range(left, left + size)) and (i in range(top, top + size))) else matrix[i][j])
    return result


def create_figure(figure):
    figures = []
    for i in range(4):
        figures.append(figure)
    return figures


def action_side(figure, twos, side):
    ran = range(len(figure))
    on_wall = False
    for two in twos:
        if two[1] == 0:
            on_wall = True
    if not on_wall:
        return [(i + 1, j + side) for j in ran for i in ran if figure[i][j] == 2]
    return twos


def action_rotate(figure, twos):
    top = len(figure)
    bottom = -1
    left = len(figure)
    right = -1
    for (i, j) in twos:
        if i < top: top = i
        if j < left: left = j
        if i > bottom: bottom = i
        if j > right: right = j
    return left_rotate_in_matrix(figure, top, left, max(bottom - top, right - left) + 1)


def next_step(figure, score_object, action=None):
    if check_end(figure):
        figure = [[0 if elem == 0 else 1 for elem in line] for line in figure]
        return figure
    ran = range(len(figure))
    twos = [(i + 1, j) for j in ran for i in ran if figure[i][j] == 2]

    if action in ['left', '0']:
        twos = action_side(figure, twos, -1)
    if action in ['right', '1']:
        twos = action_side(figure, twos, +1)

    figure = [[1 if elem == 1 else 0 for elem in line] for line in figure]
    for (i, j) in twos:
        figure[i][j] = 2

    if action in ['rotate', '2']:
        figure = action_rotate(figure, twos)

    if check_end(figure):
        figure = [[0 if elem == 0 else 1 for elem in line] for line in figure]

    combo = 1
    for row, index in zip(figure, ran):
        if len([elem for elem in row if elem == 1]) == len(row):
            figure[index] = [0 for _ in row],
            score_object['score'] += combo * len(row)
            combo += 1

    return figure


def check_end(figure):
    highs = [len(figure) for _ in range(len(figure))]
    for j in range(len(figure)):
        for i in reversed(range(len(figure))):
            if figure[i][j] == 1:
                highs[j] = i
        for i in reversed(range(len(figure))):
            if (figure[i][j] == 2) and (highs[j] - 1 == i):
                return True
    return False

figures = [
    create_figure([
        [0, 2, 0],
        [2, 2, 2],
        [0, 2, 0]
    ]),
    create_figure([
        [0, 2, 0],
        [0, 2, 2],
        [2, 2, 0]
    ]),
    create_figure([
        [0, 2, 2],
        [0, 2, 0],
        [2, 2, 0]
    ]),
    create_figure([
        [0, 2, 0],
        [0, 2, 0],
        [0, 2, 0]
    ]),
    create_figure([
        [0, 2, 0],
        [0, 2, 0],
        [0, 2, 0]
    ]),
]


def add_random_figure(matrix, figures):
    pattern: list = figures[random.randint(0, len(figures) - 1)]
    figure = pattern[random.randint(0, len(pattern) - 1)]
    left_index = random.randint(0, len(matrix) - len(figure))
    for i in range(len(figure)):
        for j in range(len(figure)):
            matrix[i][left_index + j] = figure[i][j]
    return matrix




commands = {
    'start': 'старт, арт, тарт, торт, стар'.split(', '),
    'stop': 'стоп, топ, хватит, прекрати, on_interrupt'.split(', '),
    'left': 'влево, лево, левее, слева, лев'.split(', '),
    'right': 'вправо, право, правее, справа, прав, права, правы'.split(', '),
    'rotate': 'поворот, ворот, поверни, поворачивай, поворот'.split(', '),
    'bottom': 'вниз, ниже, низ'.split(', '),
}


def progress_string(user_id):
    return f"Ваш счёт: {users[user_id]['score']}." + "\n{" + draw_figure(
        users[user_id]['field']) + "}{Игровое поле вы видите ниже}" \
                                    "\nКаковы ваши следующие действия?"


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
    create_button('поворот'),
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
                    "text": "Вы уже играете\n" + progress_string(user_id),
                },
                buttons=[create_button('Старт')]
            ))
            return
        users[user_id] = create_user()
        add_random_figure(users[user_id]['field'], figures)
        self.send_as_json(create_response(
            session,
            {"text": "Да начнётся великая игра!\n" + progress_string(user_id)},
            buttons=buttons
        ))

    def answer_to_stop(self, session):
        user_id = session['user_id']
        if user_id not in users:
            return False

        game = progress_string(user_id)
        self.send_as_json(create_response(
            session,
            {
                'text': "Конец\n" + game,
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

        users[user_id]['field'] = next_step(users[user_id]['field'], users[user_id], action)
        if next_step(users[user_id]['field'], users[user_id], -1) == users[user_id]['field']:
            add_random_figure(users[user_id]['field'], figures)
        self.send_as_json(create_response(
            session,
            {"text": progress_string(user_id)},
            buttons=buttons
        ))
        return True

    def send_as_json(self, answer):
        self.wfile.write(bytes(json.dumps(answer), "utf-8"))


server_address = ('0.0.0.0', 80)
httpd = HTTPServer(server_address, MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               keyfile='/etc/letsencrypt/live/vezdedomen.mooo.com/privkey.pem',
                               certfile='/etc/letsencrypt/live/vezdedomen.mooo.com/fullchain.pem',
                               ssl_version=ssl.PROTOCOL_TLS)
print(server_address)
httpd.serve_forever()
