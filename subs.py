import os
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


def dictionary_parser(path):
    dictionary = {}
    with codecs.open(path, 'r', 'utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if not parts:
                continue
            words, translation, type = parts
            variants = words.split(';')
            print str([words, translation, type]).encode('utf-8')
            for variant in variants:
                translations = dictionary.setdefault(variant.strip().capitalize(), {}).setdefault(type, [])
                for variant in translation.split(';'):
                    translations.append(variant.strip().capitalize())
    return dictionary


def lingvo_parser(path):
    import xml.etree.ElementTree as ET
    import pickle
    dictionary = {}

    def deep_search(root, name):
        for el in root:
            if el.tag == name:
                yield el
            else:
                for res in deep_search(el, name):
                    yield res

    def get_text(el):
        return ' '.join([child.tail for child in el if child.tail] + ([el.text] if el.text else []))

    def handle_block(block):
        if not block:
            return
        root = ET.fromstring(('<r>%s</r>' % block).encode('utf-8'))
        translation = None
        krefs = []
        for el in root:
            if 'k' == el.tag:
                name = get_text(el).strip().lower()
                translation = dictionary.setdefault(name, [])
            elif 'dtrn' == el.tag:
                translation.append(get_text(el).strip())
            elif 'ex' == el.tag:
                translation.append(el.text)
            elif 'kref' == el.tag:
                krefs.append(el)
            else:
                for kref in deep_search(el, 'kref'):
                    krefs.append(kref)
                for dtrn in deep_search(el, 'dtrn'):
                    translation.append(get_text(dtrn).strip())

        if not translation:
            if krefs:
                for kref in krefs:
                    ref = get_text(kref).strip().lower()
                    if ref != name:
                        translation.append('^:' + ref)
        if not translation:
            print 'no translation:', name.encode('utf-8')

    if os.path.exists(path+'.pcl'):
        with open(path + '.pcl', 'rb') as file:
            dictionary = pickle.load(file)
    else:
        with codecs.open(path, 'r', 'utf-8') as file:
            block = []
            for line in file:
                line = line.strip()
                if '<k>' in line:
                    parts = line.split('<k>', 1)
                    block.append(parts[0])
                    handle_block('\n'.join(block))
                    block = ['<k>' + parts[1]]
                else:
                    block.append(line)
        with open(path+'.pcl', 'wb') as file:
            pickle.dump(dictionary, file, protocol=pickle.HIGHEST_PROTOCOL)

    return dictionary

def main():
    #en_ru = dictionary_parser(os.path.join(os.path.dirname(__file__), 'english-russian.txt'))
    #read(english_replacements, english_suffixes, sub_parser, en_ru)

    en_ru = lingvo_parser(r'c:\Users\araud\Downloads\Dictionaries\LingvoUniversalEnRu.dict')
    read(r'c:\Users\araud\Downloads\Ray.2004.BDRip.1080p.DTS.AC3.x264-CRiSC.srt', english_replacements, english_suffixes, sub_parser, en_ru)

    """
    sp_ru = lingvo_parser(r'c:\Users\araud\Downloads\Spanish\UniversalEsRu.dict')
    read(r'c:\temp\SpanishBible\b_spanish_mod_utf-8.txt', spanish_replacements, spanish_suffixes, bible_parser, sp_ru)
    """

def read(path, replacements, suffixes, parser, dictionary):
    global all_words
    with codecs.open(path, 'r', 'utf-8') as file:
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
            def normalize(lst):
                for el in lst:
                    res = el.strip()
                    if res:
                        if res.startswith('^:'):
                            res = '\t|\t'.join(normalize(dictionary.get(res[2:], []))).strip()
                        yield res
            translation = '\t|\t'.join(normalize(dictionary.get(word, [])))
            if not translation:
                continue
            print ('%s\t%s' % (word.capitalize(), translation)).encode('utf-8')
            if not total_max:
                break
            total_max -= 1


if __name__ == '__main__':
    main()
