jtalk.py
=========

日本語テキスト読み上げCLIツール。
**Ubuntu 20.04で動作確認**。

特徴

* 英単語もカタカナ読みにするオプション(--yomi)
* 読み上げている箇所を表示するオプション(-t)
* Markdownに対応（markdownのマークアップを適切に読み飛ばす）

## セットアップ

(1) Open JTalkのセットアップ
```sh
sudo apt-get install open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001
```

(2) 音声ファイルのセットアップ

```sh
wget https://sourceforge.net/projects/mmdagent/files/MMDAgent_Example/MMDAgent_Example-1.8/MMDAgent_Example-1.8.zip/download -O MMDAgent_Example-1.8.zip
unzip MMDAgent_Example-1.8.zip
sudo cp -r MMDAgent_Example-1.8/Voice/mei/ /usr/share/hts-voice
```

(3) jtalk.pyのインストール

```sh
python3 -m pip install git+https://github.com/tos-kamiya/jtalk.py
```

### アンインストール

```sh
python3 -m pip uninstall jtalk.py
```

## 利用法

コマンドラインから

```sh
jtalk.py [オプション] [テキストファイル]
```

「テキストファイル」を指定しなかった場合は現在の日時を読み上げます。
パイプからテキストを読み込むには「-」を指定してください(例2を参照)。

オプション

```sh
  -r SPEED  読み上げ速度[default: 1.0]
  -g VOL    読み上げ音量[default: 10.0]
  -t        発声されているテキストを表示する
  -j        日本語が含まれない行をスキップする
  -y, --yomi    英単語を読み（カタカナ）に変換する
  -N        改行で文を区切らないようにする
  --markdown    入力テキストがmarkdownであるとして扱う
```

（例1） このファイルを読み上げさせる例

```sh
jtalk.py -t -j README.md
```

（例2） ウェブページを読み上げさせる例（別途lynxが必要）

```sh
lynx -dump -nolist https://toshihirokamiya.com/index-j.html | jtalk.py -t -j --yomi -
```

## ライセンス

スクリプト`jtalk.py`の読み上げ機能部分は次から流用しています。
それから拡張した部分に関してはパブリックドメインといたします。

https://qiita.com/kkoba84/items/b828229c374a249965a9
