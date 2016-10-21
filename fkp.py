from ILikeItBot import ILikeItBot, read_list
import sys
import time
import argparse

reload(sys)
sys.setdefaultencoding('utf8')

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

    black_list = read_list(args.blacklist)

    print "White list:", len(white_list), "Black list:", len(black_list)
    likes_limit = 450
    sleep_seconds = 20
    count = 0

    with open(args.blacklist, 'a') as nbl:
        while likes_limit > 0:
            bot = ILikeItBot(args.app, args.user, args.password, args.proxy)
