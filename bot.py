from os import system
from datetime import datetime
import subprocess

try:
    import requests
    import vk_api
except ImportError:
    system('pip install -r requirements.txt')
    import vk_api
    import requests

config = {
    "login": '',
    "password": ''
}


# Аунтефикация в вк
def vk_login() -> vk_api.VkApi.get_api:
    try:
        vk_session = vk_api.VkApi(login=config['login'], password=config['password'], app_id=6287487, scope=1073737727)
        vk_session.auth()
        print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}]"
              f" \033[1;31m[INFO]\033[0m Successful authentication")
        return vk_session.get_api()
    except Exception as e:
        print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[1;31m[ERROR]\033[0m {e}")
        exit()


# Парсит ссылку и возваращает кортеж (тип поста, id владельца, id поста)
def parse_url(post_id: str) -> tuple[str, str, str]:
    if "wall" in post_id and not ("photo" in post_id or "video" in post_id):
        post_id = post_id.rsplit("wall")[-1].rsplit("%")[0]
        return "post", post_id.rsplit("_")[0], post_id.rsplit("_")[1]
    elif "photo" in post_id:
        photo_id = post_id.rsplit("photo")[-1].rsplit("%")[0]
        return "photo", photo_id.rsplit("_")[0], photo_id.rsplit("_")[1]
    elif "video" in post_id:
        video_id = post_id.rsplit("video")[-1].rsplit("%")[0]
        return "video", video_id.rsplit("_")[0], video_id.rsplit("_")[1]


# Проверяет поставлен ли лайк и возвращает кортеж (is_like, тип поста, id владельца, id поста)
def is_liked(vk: vk_api.VkApi.get_api, post_id: str) -> tuple[bool, str, str, str]:
    type_post, owner_id, post_id = parse_url(post_id)
    return vk.likes.isLiked(type=type_post, owner_id=owner_id, item_id=post_id)['liked'], type_post, owner_id, post_id


# Лайкает пост по ссылке
def like_post(vk, url: str) -> None:
    try:
        post_id = url.rsplit('/')[-1]
        is_like, type_post, owner_id, post_id = is_liked(vk, post_id)
        if not is_like:
            vk.likes.add(type=type_post, owner_id=owner_id, item_id=post_id)
            print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[0m[INFO] Liked post")
            return
        print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[0m[INFO] Post was liked before")
    except Exception as e:
        print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[1;31m[ERROR]\033[0m {e}")


# Загружает документ и возвращает его индификатор
def upload_file(vk: vk_api.VkApi.get_api, path: str) -> str:
    upload_url = vk.docs.getWallUploadServer()['upload_url']
    with open(path, 'rb') as document_file:
        response = requests.post(upload_url, files={'file': document_file})
        upload_result = response.json()
    document_data = vk.docs.save(**upload_result)
    return f'doc{document_data["doc"]["owner_id"]}_{document_data["doc"]["id"]}'


# Комментирует пост по ссылке
def comment_post(vk, url: str) -> None:
    try:
        type_post, owner_id, post_id = parse_url(url.rsplit('/')[-1])
        message = input(
            f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[2;33m[INPUT]\033[0m Enter your message: ")
        '''doc_path = input(
            f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[2;33m[INPUT]\033[0m Enter path to doc: ")
        doc_id = upload_file(vk, doc_path)'''
        if type_post == "post":
            vk.wall.createComment(owner_id=owner_id, post_id=post_id, message=message),
            # attachments=doc_id if doc_id else None)
            print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[0m[INFO] Comment was send")
            return
        elif type_post == "photo":
            vk.photos.createComment(owner_id=owner_id, photo_id=post_id, message=message)
            # attachments=doc_id if doc_id else None)
            print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[0m[INFO] Comment was send")
            return
        elif type_post == "video":
            vk.video.createComment(owner_id=owner_id, video_id=post_id, message=message)
            # attachments=doc_id if doc_id else None)
            print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[0m[INFO] Comment was send")
            return
        raise Exception
    except Exception as e:
        print(f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[1;31m[ERROR]\033[0m {e}")


def main():
    vk = vk_login()
    while True:
        url = input(
            f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[2;33m[INPUT]\033[0m Enter the url: ")
        choice = input(
            f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[2;33m[INPUT]\033[0m 1. Like post\n"
            f"                                     2. Comment post\n"
            f"                                     Enter value: ")
        if choice == "1":
            like_post(vk, url)
        elif choice == "2":
            comment_post(vk, url)
        else:
            print(
                f"\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[1;31m[ERROR]\033[0m Invalid choice")


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print(f"\n\033[2;36m[{datetime.now().strftime('%H:%M:%S.%f %d.%m.%Y')}] \033[0m[INFO] Bot was stopped")
