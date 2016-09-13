import vk
import os
import sys
import time
import argparse

reload(sys)
sys.setdefaultencoding('utf8')


class ILikeItBot:
    def __init__(self, app_id, user, password):
        class AuthSession(vk.AuthSession):
            def __init__(self):
                vk.AuthSession.__init__(self, app_id=app_id, user_login=user, user_password=password, scope='wall,offline')

            def get_captcha_key(self, captcha_image_url):
                print('Open CAPTCHA image url: ', captcha_image_url)
                captcha_key = raw_input('Enter CAPTCHA key: ')
                return captcha_key
        # session = vk.AuthSession(app_id=app_id, user_login=user, user_password=password, scope='wall,offline')
        session = AuthSession()
        self.api = vk.API(session, v='5.53', lang='ru', timeout=10)  # 5.35

    def online_users_from_group(self, group_id):
        fields = 'id,blacklisted,is_friend,can_send_friend_request,followers_count'
        age_step = 1
        for age in range(30, 40, age_step):
            for sex in [1, 2]:
                users = self.api.users.search(
                    count=1000, online=1, age_from=age, age_to=age+age_step, fields=fields, group_id=group_id, sex=sex
                )
                for user in users['items']:
                    yield user

    def get_avatar(self, user_id):
        return self.api.photos.get(owner_id=user_id, album_id='profile')

    def like_post(self, owner_id, post_id):
        return self.api.likes.add(type='post', owner_id=owner_id, item_id=post_id)

    def repost(self, item, where):
        return self.api.wall.repost(object='wall%d_%d' % (item['owner_id'], item['id']), group_id=where)

    def get_own_posts(self, owner_id):
        return self.api.wall.get(owner_id=owner_id, filter='owner', count='100')

    def get_user_info(self, id):
        return self.api.users.get(user_ids=id, fields='counters,online')[0]

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--app", required=True, help='vk app id')
    parser.add_argument("-u", "--user", required=True, help='vk user')
    parser.add_argument("-p", "--password", required=True, help='vk password')
    parser.add_argument("-b", "--blacklist", required=True, help='path to handled ids list')
    parser.add_argument("-w", "--whitelist", required=True, help='path to white list of ids')
    parser.add_argument("-g", "--group", required=True, help='path to white list of ids')
    parser.add_argument("-i", "--invite", required=True, help='group id where to invite')
    parser.add_argument("-r", "--repost", required=True, help='group id where to repost')

    args = parser.parse_args(sys.argv[1:])

    white_list = read_list(args.whitelist)
    black_list = read_list(args.blacklist)
    likes_limit = 499
    sleep_seconds = 7
    count = 0
    with open(args.blacklist, 'a') as nbl:
        bot = ILikeItBot(args.app, args.user, args.password)
        for user in bot.online_users_from_group(args.group):
            if (user['id'] not in white_list) or (user['id'] in black_list):
                continue

            info = bot.get_user_info(user['id'])

            if not info['online'] or info['counters']['friends'] > 700:
                continue

            count += 1
            print "vk.com/id%d:\t%d" % (user['id'], count)
            posts = bot.get_own_posts(user['id'])
            nbl.write('%d\n' % user['id'])

            for item in posts['items']:
                if not item['likes']['can_publish']:
                    continue
                text = item['text'].decode('utf-8').lower()
                if 'engl' in text or 'англ' in text:
                    print bot.repost(item, args.repost)
                    time.sleep(sleep_seconds)
                    break
            recent_posts = sorted(
                [item for item in posts['items'] if item['likes']['can_like']],
                key=lambda item: item['date'],
                reverse=True
            )
            if recent_posts:
                recent_post = recent_posts[0]
                print bot.like_post(recent_post['owner_id'], recent_post['id'])
                likes_limit -= 1
                time.sleep(sleep_seconds)
            else:
                print "No posts to like"

            avatar_images = bot.get_avatar(user['id'])
            avatars = sorted(
                avatar_images['items'],
                key=lambda item: (item['width']*item['height'] if 'width' in item else 0),
                reverse=True
            )
            if avatars:
                avatar = avatars[0]
                print bot.like_post(avatar['owner_id'], avatar['post_id'])
                likes_limit -= 1
                time.sleep(sleep_seconds)
            else:
                print "No avatars to like"

            if likes_limit <= 0:
                print "Likes limit reached..."
                break

if __name__ == '__main__':
    main()
