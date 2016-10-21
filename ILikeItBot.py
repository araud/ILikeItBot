import vk
import os
import time


class ILikeItBot:
    def __init__(self, app_id, user, password, proxy):
        class AuthSession(vk.AuthSession):
            def __init__(self):
                if proxy:
                    self.proxies = {
                        "http": proxy,
                        "https": proxy
                    }
                vk.AuthSession.__init__(self, app_id=app_id, user_login=user, user_password=password, scope='wall,offline')

            def get_captcha_key(self, captcha_image_url):
                print('Open CAPTCHA image url: ', captcha_image_url)
                captcha_key = raw_input('Enter CAPTCHA key: ')
                return captcha_key
        session = AuthSession()
        self.api = vk.API(session, v='5.35', lang='ru', timeout=300)

    def online_users_from_group(self, group_id):
        fields = 'id,blacklisted,is_friend,can_send_friend_request,followers_count'
        age_step = 1
        for age in range(22, 50, age_step):
            print "Age:", age, "Step:", age_step
            for sex in [1, 2]:
                print "Gender:", sex
                try:
                    users = self.api.users.search(
                        count=1000, online=1, age_from=age, age_to=age+age_step, fields=fields, group_id=group_id, sex=sex
                    )
                except Exception as exc:
                    text = str(exc)
                    if 'limit' not in text:
                        time.sleep(5)
                        continue
                    else:
                        raise

                for user in users['items']:
                    yield user
                time.sleep(5)

    def get_avatar(self, user_id):
        while True:
            try:
                return self.api.photos.get(owner_id=user_id, album_id='profile')
            except Exception as exc:
                text = str(exc)
                if 'limit' not in text:
                    time.sleep(5)
                else:
                    raise

    def like_post(self, owner_id, post_id):
        try:
            return self.api.likes.add(type='post', owner_id=owner_id, item_id=post_id)
        except Exception as exc:
            text = str(exc)
            if 'limit' not in text:
                return text
            else:
                raise

    def repost(self, item, where):
        try:
            return self.api.wall.repost(object='wall%d_%d' % (item['owner_id'], item['id']), group_id=where)
        except Exception as exc:
            text = str(exc)
            if 'limit' not in text:
                return text
            else:
                raise

    def get_own_posts(self, owner_id):
        while True:
            try:
                return self.api.wall.get(owner_id=owner_id, filter='owner', count='100')
            except Exception as exc:
                text = str(exc)
                if 'limit' not in text:
                    time.sleep(5)
                else:
                    raise

    def get_user_info(self, id, fields='counters,online'):
        while True:
            try:
                return self.api.users.get(user_ids=id, fields=fields)[0]
            except Exception as exc:
                text = str(exc)
                if 'limit' not in text:
                    time.sleep(5)
                else:
                    raise

    def invite_to_group(self, id, group):
        pass


def read_list(path):
    res = set()
    if not os.path.exists(path):
        return res
    with open(path, 'r') as file:
        for line in file:
            if not line.strip().isalnum():
                continue
            res.add(int(line))
    return res
