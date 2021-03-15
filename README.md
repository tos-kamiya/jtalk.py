jtalk.py
=========

日本語テキスト読み上げスクリプト（オレオレ仕様）。Ubuntu 20.04で動作確認

## セットアップ

(1) Docoptのインストール

```sh
sudo python3 -m pip install docopt
```

(2) Open JTalkのセットアップ
```
sudo apt-get install open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001
```

(3) 音声ファイルのセットアップ

```
wget https://sourceforge.net/projects/mmdagent/files/MMDAgent_Example/MMDAgent_Example-1.8/MMDAgent_Example-1.8.zip/download -O MMDAgent_Example-1.8.zip
unzip MMDAgent_Example-1.8.zip
sudo cp -r MMDAgent_Example-1.8/Voice/mei/ /usr/share/hts-voice
```

(4) パスが通ったディレクトリ、ファイル`jtalk.py`と`jtalkpy_eng_yomi_data.tsv`をコピーする

## 利用法

コマンドラインから

```sh
jtalk.py [オプション] [テキストファイル]
```

「テキストファイル」を指定しなかった場合は現在の日時を読み上げます。
パイプからテキストを読み込むには「-」を指定してください。

オプション

```sh
  -t        発声されているテキストを表示する
  -j        日本語が含まれない行をスキップする
  --yomi    英単語を読み（カタカナ）に変換する
  -N        改行で文を区切らないようにする
```

（例） このファイルを読み上げさせる例

```sh
jtalk.py -t -j README.md
```

（例） ウェブページを読み上げさせる例（別途lynxが必要）

```sh
lynx -dump -nolist https://toshihirokamiya.com/index-j.html | jtalk.py -t -j --yomi -
```

## ライセンス

同梱ファイル`jtalkpy_eng_yomi_data.tsv`のライセンスは次の元データのライセンスに従います。

https://github.com/KEINOS/google-ime-user-dictionary-ja-en

スクリプト`jtalk.py`の読み上げ機能部分は次から流用しています。
それから拡張した部分に関してはパブリックドメインといたします。

https://qiita.com/kkoba84/items/b828229c374a249965a9

## 開発

### jtalkpy_eng_yomi_data.tsvを生成する方法

このjtalk.pyリポジトリをgit cloneし、

https://github.com/tos-kamiya/jtalk.py

ルートディレクトリで次のリポジトリをgit cloneして、

https://github.com/KEINOS/google-ime-user-dictionary-ja-en

`gen_eng_yomi_data.py`を実行してください。

