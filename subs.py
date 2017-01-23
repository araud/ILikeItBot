import sys
import codecs

all_words = {}

english_replacements = [('-', ' '), ("'re", ' are'), ("'ve", ' have'), ("n't", ' not'), ("'ll", ' will'), ("'m", ' am')]
english_suffixes = ['s', 'ing', 'd', 'ed']

spanish_replacements = []
spanish_suffixes = [u's', u'n', u'is', u'a', u'do', u'ba', u'es', u'on', u'á', u'r', u'mente', u'mos', u'o', u'd', u'ban', u'da', u'emos', u'te', u'e', u'la', u'le', u'lo', u'an', u'itas', u'as', u'os', u'los', u'ción', u'res', u'án', u'el', u'me', u'se', u'l', u'i', u'las', u'das', u'dos', u'les', u'm', u'cia', u'ron', u'ta', u'en', u'ás', u'tas', u'ita', u'é', u'ra', u'b', u'na', u'dor', u'rá', u'teis', u'dad', u'sa', u'ble', u'que', u't', u'so', u'nte', u'monos', u'eo', u'am', u'nos', u'c', u'za', u'idad', u'ndo', u'ad', u'ma', u'ga', u'de', u'at', u'no', u'samente', u'eos', u'ías', u'or', u'ro', u'jo', u'ncia', u'aim', u'je', u'nes']


def handle_text(text, replacements):
    global all_words
    for wht, wth in replacements:
        text = text.replace(wht, wth)
    for word in text.split():
        word = word.lower()
        for sym in ['.', "'", '"', ',', ';', '?', '!', '<i>', '</i>', '(', ')', '{', '}', ':', '-']:
            word = word.replace(sym, '')
        for sym in word:
            if sym.lower() == sym.upper():
                word = word.replace(sym, '')
        all_words.setdefault(word, 0)
        all_words[word] += 1


def sub_parser(line, replacements, statics={'lines': []}):
    lines = statics['lines']
    line = line.strip()
    if '-->' in line:
        handle_text('\n'.join(lines[:-1]), replacements)
        lines = []
    else:
        lines.append(line)


def bible_parser(line, replacements):
    parts = line.strip().split('\t')
    handle_text(parts[-1], replacements)


def main():
    # read(english_replacements, english_suffixes, sub_parser)
    read(spanish_replacements, spanish_suffixes, bible_parser)


def read(replacements, suffixes, parser):
    global all_words
    with codecs.open(sys.argv[1], 'r', 'utf-8') as file:
        for line in file:
            parser(line, replacements)
    forms = {}
    for suffix in suffixes:
        for word in all_words.iterkeys():
            suffix_len = len(suffix)
            if word.endswith(suffix) and word[:-suffix_len] in all_words and (len(word) - suffix_len) > 1:
                forms[word] = word[:-suffix_len]
    for form, word in forms.iteritems():
        if form in all_words and word in all_words:
            all_words[word] += all_words[form]
            del all_words[form]
    words = list(all_words.iteritems())
    print '-------------------------------------------'
    sbw = sorted(words, key=lambda (word, _): word)
    prev = ''
    suffixes = {}
    for word, count in sbw:
        if prev in word and word and prev:
            suffix = word.replace(prev, '')
            suffixes.setdefault(suffix, 0)
            suffixes[suffix] += 1
        prev = word
    suffixes = sorted(suffixes.iteritems(), key=lambda(_, count): count, reverse=True)
    print '-------------------------------------------'
    for suff, count in suffixes:
        if count > 3:
            print "u'%s'," % suff.encode('utf-8'),
    print
    for suff, count in suffixes:
        print suff.encode('utf-8'), count

    print '-------------------------------------------'
    words.sort(key=lambda(_, count): count, reverse=True)
    for word, count in words:
        print '%d\t%s' % (count, word.encode('utf-8'))
    print '-------------------------------------------'
    print 'Total: ', len(words)
    print '-------------------------------------------'
    total_max = 2000
    for word, count in words:
        if count > 1 and word.strip():
            print word.encode('utf-8').capitalize()
            if not total_max:
                break
            total_max -= 1


if __name__ == '__main__':
    main()
