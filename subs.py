import sys
import codecs

all_words = {}


def handle_text(text):
    global all_words
    for wht, wth in [('-', ' '), ("'re", ' are'), ("'ve", ' have'), ("n't", ' not'), ("'ll", ' will'), ("'m", ' am')]:
        text = text.replace(wht, wth)
    for word in text.split():
        word = word.lower()
        for sym in ['.', "'", '"', ',', ';', '?', '!', '<i>', '</i>', '(', ')', '{', '}']:
            word = word.replace(sym, '')
        all_words.setdefault(word, 0)
        all_words[word] += 1


def main():
    global all_words
    lines = []
    with codecs.open(sys.argv[1], 'r', 'utf-8') as file:
        for line in file:
            line = line.strip()
            if '-->' in line:
                handle_text('\n'.join(lines[:-1]))
                lines = []
            else:
                lines.append(line)
    forms = {}
    for word in all_words.iterkeys():
        for suffix in ['s', 'ing', 'd', 'ed']:
            suffix_len = len(suffix)
            if word.endswith(suffix) and word[:-suffix_len] in all_words and (len(word) - suffix_len) > 1:
                forms[word] = word[:-suffix_len]
    for form, word in forms.iteritems():
        all_words[word] += all_words[form]
        del all_words[form]
    words = list(all_words.iteritems())
    words.sort(key=lambda(_, count): count, reverse=True)
    for word, count in words:
        print '%d\t%s' % (count, word.encode('utf-8'))
    print '-------------------------------------------'
    print 'Total: ', len(words)
    print '-------------------------------------------'
    for word, count in words:
        if count > 1:
            print word.encode('utf-8').capitalize()


if __name__ == '__main__':
    main()
