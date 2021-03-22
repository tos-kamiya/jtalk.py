#!/usr/bin/env python3

# 参考
# https://qiita.com/kkoba84/items/b828229c374a249965a9
# https://mekou.com/linux-magazine/open-jtalklinux-%E6%97%A5%E6%9C%AC%E8%AA%9E%E9%9F%B3%E5%A3%B0%E5%90%88%E6%88%90%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%B3/
# https://minus9d.hatenablog.com/entry/2015/07/16/231608
# https://github.com/cod-sushi/alkana.py/blob/master/README_ja.md

# Ubuntu 20.04で動作検証

SETUP = """
# (1) Docoptのインストール
sudo python3 -m pip install docopt

# (2) Open JTalkのセットアップ
sudo apt-get install open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001

# (3) 音声ファイルのセットアップ
wget https://sourceforge.net/projects/mmdagent/files/MMDAgent_Example/MMDAgent_Example-1.8/MMDAgent_Example-1.8.zip/download -O MMDAgent_Example-1.8.zip
unzip MMDAgent_Example-1.8.zip
sudo cp -r MMDAgent_Example-1.8/Voice/mei/ /usr/share/hts-voice

# (4) alkanaのインストール
sudo python3 -m pip install alkana
"""

import os
import re
import sys
import subprocess
import unicodedata

from alkana import get_kana
from docopt import docopt


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


def speech_lines(lines, shown_lines=None, speed=None, volume=None):
    open_jtalk = ['open_jtalk']
    mech = ['-x', '/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice = ['-m', '/usr/share/hts-voice/mei/mei_normal.htsvoice']
    s = ['-r', '%g' % (1.0 if speed is None else speed)]
    v = ['-g', '%g' % (10.0 if volume is None else volume)]
    outwav = ['-ow']
    wav_gen_cmd = open_jtalk + mech + htsvoice + s + v + outwav
    play_cmd = ['aplay','-q']

    speech_process = None
    for i, L in enumerate(lines):
        wav_file = wav_file_template % (i % 2)
        c = subprocess.Popen(wav_gen_cmd + [wav_file], stdin=subprocess.PIPE)
        c.stdin.write(L.encode())
        c.stdin.close()
        c.wait()
        if speech_process is not None:
            speech_process.wait()
        if shown_lines:
            print(shown_lines[i], file=sys.stderr)
        speech_process= subprocess.Popen(play_cmd + [wav_file])
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
  -r SPEED  読み上げ速度[default: 1.0]
  -g VOL    読み上げ音量[default: 10.0]
  -t        発声されているテキストを表示する
  -j        日本語が含まれない行をスキップする
  --yomi    英単語を読み（カタカナ）に変換する
  -N        改行で文を区切らないようにする
"""


def main():
    args = docopt(__doc__)
    if not args['<textfile>']:
        text = now_text()
    elif args['<textfile>'] == '-':
        text = sys.stdin.read()
    else:
        with open(args['<textfile>']) as inp:
            text = inp.read()

    speed = float(args['-r']) if args['-r'] else None
    volume = float(args['-g']) if args['-g'] else None

    lines = parse_lines(text, marge_lines=args['-N'])

    if args['-j']:
        lines = [L for L in lines if includes_japanese(L)]

    if args['--yomi']:
        yomi_lines = [convert_english_words(L) for L in lines]
        speech_lines(yomi_lines, shown_lines=args['-t'] and lines, speed=speed, volume=volume)
    else:
        speech_lines(lines, shown_lines=args['-t'] and lines, speed=speed, volume=volume)


if __name__ == '__main__':
    main()