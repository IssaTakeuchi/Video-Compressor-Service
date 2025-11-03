# Video-Compressor-Service

## 概要 
CLIにて動画圧縮を行う。クライアントからサーバーに動画ファイルと操作を送信し、処理が完了すればサーバーからクライアントに処理されたファイルが返される。実行可能な操作は、以下の通り。
- 動画を圧縮する
- 動画の解像度を変更する
- 動画のアスペクト比を変更する
- 動画を音声に変換する
- 指定した時間でGIFを作成

## 環境
- ![Python](https://img.shields.io/badge/-Python-F9DC3E.svg?style=flat&logo=python)： 3.12.3
- ![Linux](https://img.shields.io/badge/-Linux-FCC624?style=flat&logo=linux&logoColor=black)：Ubuntu 24.04.2

## ffmpegの使用
### インストール手順
- APTを使用してffmpegのインストール

`sudo apt install ffmpeg`

- pythonの仮想環境をactivate状態にする 

`source bin/activate`

- pythonから使用するためのラッパーライブラリをインストール

`pip install ffmpeg-python`