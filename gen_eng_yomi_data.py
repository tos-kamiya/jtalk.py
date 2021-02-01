import sys
import os
import re
import unicodedata


from jtalk import ENG_YOMI_DATA_FILE


_script_dir = os.path.dirname(os.path.realpath(__file__))

JISHO_DATA_DIR_PATH = ["google-ime-user-dictionary-ja-en-master", "Google-ime-jp-カタカナ英語辞典"]

JISHO_DATA_FILES = ['google-ime-jp-カタカナ英語辞書01-あ～お(1).txt',
    'google-ime-jp-カタカナ英語辞書02-おぞん～さばら.txt',
    'google-ime-jp-カタカナ英語辞書03-さはりん～でぃんぎー.txt',
    'google-ime-jp-カタカナ英語辞書04-でぃんご～ひっぷ.txt',
    'google-ime-jp-カタカナ英語辞書05-ひっぷ～みすたいぷ.txt',
    'google-ime-jp-カタカナ英語辞書06-みずだこ～んびら.txt',
]


def is_kana_word(s):
    for ch in s:
        if not (ch == '\u30FC' or "KATAKANA" in unicodedata.name(ch)):
            return False
    return True


data_dir_path = JISHO_DATA_DIR_PATH
while len(data_dir_path) > 0 and not os.path.isdir(os.path.join(*data_dir_path)):
    data_dir_path = data_dir_path[1:]

# いんでぃー	indie	名詞	インディー
# あんぺら	Machaerina rubiginosa (species of tropical sedge) (may: ampela)	名詞	アンペラ

eng_to_yomi = dict()

for f in JISHO_DATA_FILES:
    p = os.path.join(*data_dir_path, f)
    with open(p) as inp:
        for L in inp:
            fields = L.rstrip().split('\t')
            if len(fields) == 4:
                y = fields[3]
            elif len(fields) == 3:
                y = fields[1]
            else:
                assert len(fields) not in (3, 4)
            e = fields[1]
            e = re.sub(' *[(].*[)] *$', '', e)
            if is_kana_word(y) and ' ' not in e and e not in eng_to_yomi:
                eng_to_yomi[e] = y

with open(os.path.join(_script_dir, ENG_YOMI_DATA_FILE), 'w') as outp:
    for e, y in sorted(eng_to_yomi.items()):
        print("%s\t%s" % (e, y), file=outp)
