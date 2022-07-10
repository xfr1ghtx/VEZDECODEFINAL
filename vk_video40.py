import re

from vk_api_requests import get_response

with open("secret.txt", 'r') as f:
    token = str(f.readline())[:-1]


def check_comments(owner_id, video_id, answers):
    response = get_response("video.getComments", token, owner_id=owner_id, video_id=video_id)
    vocab = {key: 0 for key in answers}
    for item in answers:
        for answer in answers:
            if bool(re.match(answer, item['text'])):
                vocab[answer] += 1
                break

    return vocab


owner_id = int(input("Введите id группы"))
video_id = int(input("Введите id видео"))
answers = input("Введите шаблоны шаблоны сообщений, разделяя их последовательностью |||").split("|||")

