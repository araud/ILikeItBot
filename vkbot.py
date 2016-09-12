import vk
import os
import sys
import time
import argparse


class ILikeItBot:
    def __init__(self, app_id, user, password):
        session = vk.AuthSession(app_id=app_id, user_login=user, user_password=password, scope='wall,offline')
        self.api = vk.API(session, v='5.53', lang='ru', timeout=10)  # 5.35

    def online_users_from_group(self, group_id):
        offset = 0
        while True:
            users = self.api.users.search(count=1000, online=1, age_from=20, fields='id', group_id=group_id)
            offset += len(users['items'])
            for user in users['items']:
                yield user
            if offset > users['count']:
                break

    def get_avatar(self, user_id):
        return self.api.photos.get(owner_id=user_id, album_id='profile')

    def like_post(self, owner_id, post_id):
        # return self.api.likes.add(type='post', owner_id=owner_id, item_id=post_id, access_key=self.access_token)
        return self.api.likes.add(type='post', owner_id=owner_id, item_id=post_id)

    def get_own_posts(self, owner_id):
        return self.api.wall.get(owner_id=owner_id, filter='owner', count='100')


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

    args = parser.parse_args(sys.argv[1:])

    white_list = read_list(args.whitelist)
    black_list = read_list(args.blacklist)

    with open(args.blacklist, 'a') as nbl:
        bot = ILikeItBot(args.app, args.user, args.password)
        for user in bot.online_users_from_group(args.group):
            if (user['id'] not in white_list) or (user['id'] in black_list):
                continue
            nbl.write('%d\n' % user['id'])
            print "vk.com/id%d" % user['id']
            posts = bot.get_own_posts(user['id'])
            recent_posts = sorted(
                [item for item in posts['items'] if item['likes']['can_like']],
                key=lambda item: item['date'],
                reverse=True
            )
            if recent_posts:
                recent_post = recent_posts[0]
                print bot.like_post(recent_post['owner_id'], recent_post['id'])
                time.sleep(5)
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
                time.sleep(5)
            else:
                print "No avatars to like"

if __name__ == '__main__':
    main()
