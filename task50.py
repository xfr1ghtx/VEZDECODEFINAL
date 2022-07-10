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

field_size = 4


def create_user():
    return {
        'matrix': [[0 for _ in range(field_size)] for __ in range(field_size)],
        'score': 0,
        'end': False
    }


def get_random_empty_cell(matrix):
    cell = random.randint(0, field_size - 1), random.randint(0, field_size - 1)
    i = 0
    while (matrix[cell[0]][cell[1]] != 0) and (i < 100):
        cell = random.randint(0, field_size - 1), random.randint(0, field_size - 1)
        i += 1
    if i == 100:
        cell = [(i, j) for i in range(len(matrix)) for j in range(len(matrix)) if matrix[i][j] == 0]
        if len(cell) == 0:
            return None
        cell = cell[0]
    return cell


def draw(matrix, score, step=5):
    return f'Ваш счёт: {score}\n' + "{"\
           f'{(len(matrix) * (step * " " + "|"))[:-1]}\n' + \
           f'\n{(len(matrix) * (step * "_" + "|"))[:-1]}\n{(len(matrix) * (step * " " + "|"))[:-1]}\n' \
               .join(['|'.join([str(elem if elem != 0 else " ").center(step, " ") for elem in row]) for row in matrix]) + \
           f'\n{(len(matrix) * (step * " " + "|"))[:-1]}' + "}{}"


def step(matrix, score_object):
    new_rows = []
    for row in matrix:
        if sum(row) == 0:
            new_rows.append(row)
            continue
        new_row = []
        for i in range(4):
            if row[i] != 0:
                new_row.append(row[i])
        new_row += [0] * (len(matrix) - len(new_row))
        for i in range(len(matrix) - 1):
            if new_row[i] == new_row[i + 1]:
                new_row[i] = new_row[i] * 2
                score_object['score'] += new_row[i]
                new_row.pop(i + 1)
                new_row.append(0)
        new_rows.append(new_row)
    return new_rows


def left_step(matrix, score_object):
    return step(matrix, score_object)


def right_step(matrix, score_object):
    inverse = [list(reversed(row)) for row in matrix]
    return [list(reversed(row)) for row in step(inverse, score_object)]


def top_step(matrix, score_object):
    rotated = [list(t) for t in [*zip(*matrix)]]
    return [list(t) for t in [*zip(*step(rotated, score_object))]]


def bottom_step(matrix, score_object):
    rotated = [list(t) for t in [*zip(*matrix)]]
    return [list(t) for t in [*zip(*right_step(rotated, score_object))]]


def next_step(game_object, action=None):
    matrix = game_object['matrix']
    if action == 'left': matrix = left_step(matrix, game_object)
    if action == 'right': matrix = right_step(matrix, game_object)
    if action == 'top': matrix = top_step(matrix, game_object)
    if action == 'bottom': matrix = bottom_step(matrix, game_object)
    new_cell = get_random_empty_cell(matrix)
    if new_cell is None:
        game_object['end'] = True
    else:
        new_val = random.randint(1, 2) * 2
        matrix[new_cell[0]][new_cell[1]] = new_val
    game_object['matrix'] = matrix
    return draw(matrix, game_object['score'])


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
                    "text": "Вы уже играете\n" + draw(users[user_id]['matrix'], users[user_id]['score']),
                },
                buttons=[create_button('Старт')]
            ))
            return
        users[user_id] = create_user()
        users[user_id]['matrix'][0][0] = 2
        self.send_as_json(create_response(
            session,
            {"text": "Да начнётся великая игра!\n" + draw(users[user_id]['matrix'], users[user_id]['score'])},
            buttons=buttons
        ))

    def answer_to_stop(self, session):
        user_id = session['user_id']
        if user_id not in users:
            return False

        self.send_as_json(create_response(
            session,
            {
                'text': "Конец\n" + draw(users[user_id]['matrix'], users[user_id]['score']),
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
                {"text": f"Вы проиграли( \n"
                         f"{new_step}"},
                buttons=[create_button('Старт')]
            ))
            del (users[user_id])
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
