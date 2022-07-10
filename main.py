import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import vk_api_requests

with open("secret.txt", 'r') as f:
    token = str(f.readline())[:-1]
    secret_answer = str(f.readline())[:-1]
    super_secret_token = str(f.readline())

users = {}


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
        print(body)
        if (body["type"] == "confirmation") and (body["group_id"] == 213734019):
            self.wfile.write(bytes(secret_answer, "utf-8"))
            return

        if body["type"] == "message_new":
            message = body['object']['message']
            who = message['from_id']
            text = message['text']
            if text == "Звонок":
                new_call = vk_api_requests.get_response("messages.startCall", super_secret_token)
                vk_api_requests.get_response("messages.send", token,
                                             peer_id=who,
                                             random_id=random.randint(0, 9999999999999999),
                                             message=new_call['response']['join_link'])
            print("ok")
            self.wfile.write(bytes("ok", "utf-8"))

        else:
            self.wfile.write(bytes("ok", "utf-8"))

    def send_as_json(self, answer):
        self.wfile.write(bytes(json.dumps(answer), "utf-8"))


server_address = ('0.0.0.0', 80)
httpd = HTTPServer(server_address, MyHTTPRequestHandler)
# httpd.socket = ssl.wrap_socket(httpd.socket,
#                                server_side=True,
#                                keyfile='/etc/letsencrypt/live/vezdedomen.mooo.com/privkey.pem',
#                                certfile='/etc/letsencrypt/live/vezdedomen.mooo.com/fullchain.pem',
#                                ssl_version=ssl.PROTOCOL_TLS)
print(443)
httpd.serve_forever()
