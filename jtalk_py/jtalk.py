#!/usr/bin/env python3

import os
import re
import sys
import subprocess
import unicodedata
import shutil
import signal

from alkana import get_kana
from docopt import docopt
import markdown
from bs4 import BeautifulSoup

import importlib.metadata
__version__ = importlib.metadata.version('jtalk.py')


# check open_jtalk installation
if not shutil.which('open_jtalk'):
    sys.exit("Error: `open_jtalk` executable is not found.")


# ref https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
def md_to_text(md):
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, features='html.parser')
    return soup.get_text()
    
    
def is_japanese(ch):
    name = unicodedata.name(ch, None)
    return name is not None and \
            ("CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name)


def includes_japanese(s):
    return any(is_japanese(ch) for ch in s)


def convert_english_words(L):
    ws = re.split(r"([a-zA-Z']+)", L)
    ys = []
    for w in ws:
        if re.fullmatch("[a-zA-Z']+", w):
            w = get_kana(w) or get_kana(w.lower()) or w
        ys.append(w)
    return ''.join(ys)


def parse_lines(text, marge_lines=False):
    if marge_lines:
        text = re.sub(r'\n\s*(?<=[a-zA-Z])', ' ', text)
        text = re.sub(r'\n\s*(?<=[^a-zA-Z])', '', text)
        text = text.replace('\n\n', '。')

    # remove spaces between zenkaku and hankaku
    text = re.sub(r'((?!\n)\s)+', ' ', text)
    s = list(text)
    for i in range(1, len(text) - 1):
        prev_ch, ch, next_ch = s[i-1], s[i], s[i+1]
        if ch == ' ':
            prev_ch_is_japanese = is_japanese(prev_ch)
            next_ch_is_japanese = is_japanese(next_ch)
            if prev_ch_is_japanese and not next_ch_is_japanese or not prev_ch_is_japanese and next_ch_is_japanese:
                s[i] = ''
    text = ''.join(s)

    lines = re.split(r"([。\n]+)", text)
    r = []
    for L in lines:
        if not L:
            pass
        elif re.fullmatch(r"[。\n]+", L):
            if r and "。" in L:
                r[-1] += "。"
        else:
            r.append(L)
    lines = r

    return lines


wav_file_template = "/tmp/open_jtalk_%d.wav"


def speech_lines(lines, shown_lines=None, speed=None, volume=None, speech_progress_index_box=None):
    open_jtalk = ['open_jtalk']
    mech = ['-x', '/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice = ['-m', '/usr/share/hts-voice/mei/mei_normal.htsvoice']
    s = ['-r', '%g' % (1.0 if speed is None else speed)]
    v = ['-g', '%g' % (10.0 if volume is None else volume)]
    outwav = ['-ow']
    wav_gen_cmd = open_jtalk + mech + htsvoice + s + v + outwav
    play_cmd = ['aplay','-q']

    if speech_progress_index_box is None:
        speech_progress_index_box = [None]
    speech_process = None
    for i, L in enumerate(lines):
        if speech_progress_index_box[0] is not None and i < speech_progress_index_box[0]:
            continue  # for i
        wav_file = wav_file_template % (i % 2)
        c = subprocess.Popen(wav_gen_cmd + [wav_file], stdin=subprocess.PIPE)
        c.stdin.write(L.encode())
        c.stdin.close()
        c.wait()
        if speech_process is not None:
            speech_process.wait()
        if shown_lines:
            print(shown_lines[i], file=sys.stderr)
        speech_process = subprocess.Popen(play_cmd + [wav_file])
    if speech_process is not None:
        speech_process.wait()


def now_text():
    import locale
    from datetime import datetime

    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    d = datetime.now()
    wd = d.strftime('%A')  # 曜日
    text = '%s月%s日%s、%s時%s分%s秒' % (d.month, d.day, wd, d.hour, d.minute, d.second)
    return text


__doc__ = """日本語テキストを読み上げます。

Usage:
  jtalk [options] [<textfile>]

Options:
  -n INDEX  読み上げ開始位置(0〜)
  -r SPEED  読み上げ速度[default: 1.0]
  -g VOL    読み上げ音量[default: 10.0]
  -t        発声されているテキストを表示する
  -j        日本語が含まれない行をスキップする
  -y, --yomi    英単語を読み（カタカナ）に変換する
  -N        改行で文を区切らないようにする
  --markdown    入力テキストがmarkdownであるとして扱う
"""


def main():
    args = docopt(__doc__, version=__version__)
    input_file = args['<textfile>']
    option_markdown = (input_file and input_file.endswith('.md')) or args['--markdown']

    if not input_file:
        text = now_text()
    elif input_file == '-':
        text = sys.stdin.read()
    else:
        with open(input_file) as inp:
            text = inp.read()

    speed = float(args['-r']) if args['-r'] else None
    volume = float(args['-g']) if args['-g'] else None

    if option_markdown:
        text = md_to_text(text)
    lines = parse_lines(text, marge_lines=args['-N'])

    if args['-j']:
        lines = [L for L in lines if includes_japanese(L)]

    speech_progress_index_box = [None]
    if args['-n']:
        speech_progress_index_box[0] = int(args['-n'])
    def sigint_handler(signum, frame):
        i = speech_progress_index_box[0]
        if i is not None:
            print("> 読み上げを中断しました。中断位置から再開するには、オプション`-n %d`をつけて再度実行してください。" % i, file=sys.stderr)
        sys.exit(128 + signal.SIGINT)
    signal.signal(signal.SIGINT, sigint_handler)
    
    if args['--yomi']:
        yomi_lines = [convert_english_words(L) for L in lines]
        speech_lines(yomi_lines, shown_lines=args['-t'] and lines, speed=speed, volume=volume,
            speech_progress_index_box=speech_progress_index_box)
    else:
        speech_lines(lines, shown_lines=args['-t'] and lines, speed=speed, volume=volume,
            speech_progress_index_box=speech_progress_index_box)


if __name__ == '__main__':
    main()
