import vk
import os
import sys
import time
import argparse

reload(sys)
sys.setdefaultencoding('utf8')


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


def anti_spam(args):
    bot = ILikeItBot(args.app, args.user, args.password)
    import people_base
    fields = "counters, verified, sex, bdate, city, country, home_town, has_photo, lists, site, education, universities, schools, status, last_seen, followers_count, occupation, relatives, relation, personal, connections, exports, wall_comments, activities, interests, music, movies, tv, books, games, about, quotes, can_send_friend_request, career, military"
    for id in people_base.ham_people_ids:
        print bot.get_user_info(id, fields)
        time.sleep(5)


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
    parser.add_argument("--proxy", required=True, help='proxy')

    args = parser.parse_args(sys.argv[1:])

    # XXX return anti_spam(args)

    white_list = read_list(args.whitelist)
    black_list = read_list(args.blacklist)
    print "White list:", len(white_list), "Black list:", len(black_list)
    likes_limit = 499
    sleep_seconds = 20
    count = 0
    with open(args.blacklist, 'a') as nbl:
        while likes_limit > 0:
            bot = ILikeItBot(args.app, args.user, args.password, args.proxy)
            for user in bot.online_users_from_group(args.group):
                if (user['id'] not in white_list) or (user['id'] in black_list):
                    continue
                time.sleep(5)
                info = bot.get_user_info(user['id'])

                if (not info['online']) or ('counters' not in info) or (info['counters']['friends'] > 300):
                    continue
                time.sleep(5)
                count += 1
                print "%d\tvk.com/id%d:\t%d friends" % (count, user['id'], info['counters']['friends'])
                posts = bot.get_own_posts(user['id'])
                black_list.add(user['id'])
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
                    if 'post_id' in avatar:
                        print bot.like_post(avatar['owner_id'], avatar['post_id'])
                        likes_limit -= 1
                        time.sleep(sleep_seconds)
                else:
                    print "No avatars to like"

                if likes_limit <= 0:
                    print "Likes limit reached..."
                    return


def deflate_dict(val, name=''):
    for key, value in val.iteritems():
        if isinstance(value, dict):
            for item in deflate_dict(value, name + key + '.'):
                yield item
        else:
            yield name + key, value


def remove_fields(var, fields):
    for to_remove in fields:
        if to_remove in var:
            del var[to_remove]


def features():
    import people_base
    print set(people_base.spam_people_ids).intersection(set(people_base.ham_people_ids))
    for kind in [people_base.spam_people, people_base.ham_people]:
        flat_persons = []
        for person in kind:
            remove_fields(person, ['id', 'first_name', 'last_name', 'site', 'last_seen', 'home_town', 'military', 'universities', 'schools', 'relatives', 'career', 'skype', 'instagram'])
            flat_person = dict(item for item in deflate_dict(person))
            remove_fields(flat_person, ['country.title', 'counters.online_friends', 'counters.mutual_friends', 'city.title'])
            flat_persons.append(flat_person)
        ftrs = {}
        keys = set()
        for person in flat_persons:
            for key, val in person.iteritems():
                ftrs.setdefault(key, set()).add(tuple(val) if isinstance(val, list) else val)
        print ftrs

if __name__ == '__main__':
    #features()
    main()

