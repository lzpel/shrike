# shrike
Slackのログイン時間を毎日報告するSlackBot。勤務時間の記録を残すことが目的。
## Description
```
常時ワークスペースの全メンバーのログイン状況を記録する
毎日23:59にアプリが参加するチャンネルに当日のログイン状況を書き込む
書き込み内容は以下の例のようにIDと時間帯の羅列である
smith: 18:00-19:00 19:30-22:00
dakyo: 0:00-24:00
```
## Files
- app.yaml
```
AppEngineから参照されるファイル
URLルーティングと使用言語(python2.7)と使用ライブラリを宣言

拡張子を含むpathへのリクエストは/staticディレクトリ内のファイルへ投げる
それ以外のリクエストはmain.pyへ投げる
```
- cron.yaml
```
AppEngineから参照されるファイル
定期的にサービス自身にリクエストを投げる設定を宣言
内容は以下の通り

五分毎にPOST/presence_test
- ワークスペースのメンバーのログイン状況の取得と記録を行う
毎日0:00にPOST/presence_adaymake
- 記録用のモデルをデータベース上に新規作成する
毎日23:59にPOST/presence_adaypost
- モデルに記録したログイン状況をチャンネルに書き込む
```
- deploy.sh
```
作者から手動で参照される
LINUX環境$>deploy.shとコマンドを叩けば
自動でAppEngineとGithubにアップロードされる
手を抜くためのシェルスクリプト
```
- main.py
```
app.yamlから参照
静的ファイル
サービスのメインプログラム。
最上位関数については別途で解説する
```
- README.md
```
このファイル
```
- test.py
```
作者から手動で参照されるスクリプト
ちょっとした機能を試すための砂場
```
##Directories
- static/*
```
app.yamlから参照される
URLからアクセスされる静的ファイルを格納するディレクトリ
botのアイコン画像が入っている
app.yaml内でhttps://HOSTNAME/icon.pngは/static/icon.pngと対応するように宣言されている。
```
- template/*
```
GoogleAppEngineの基本的な機能の自作ライブラリを格納するディレクトリ
/template/http.pyはリクエストを飛ばすライブラリ。例:http.get("http://google.com")
/template/unit.pyはデータベースの読み書きのライブラリ。例:unit(name="anonymous",desc="a person").put()
/template/appengine.pyはAppEngineの起動、リクエストの受信、レスポンスの作成を簡略化するライブラリ
```
## main.py のメソッド
main.pyのメソッドはリクエストハンドラかリクエストハンドラから呼び出される内部使用メソッドの2種類に分けられる。
### main.py の内部使用メソッド
- def presence_roundoff(plist, windowhalfmin):
```
勤務状況の揺らぎを補正する。
例えば1時間ログイン5分ログアウト1時間ログインを2時間のログインと見做す

plist:
ログイン1ログアウト0とした一日の勤務状況のlist
もしlen(plist)==Nなら1440/N分でサンプリングされているとみなす

windowhalfmin:
補正用の窓の幅の半分の長さを表すint。単位は分。
例としてwindowhalfmin=30の時
任意の時刻の前後30分の半分以上でログインしている場合
補正後のデータでもその時刻にログインしていたとみなす

return:
勤務状況のlist。フォーマットと長さはplistと一致する
```
def presence_timetext(plist):
```
勤務状況のlistを表すstrを返す
正午以降ログインし続けていることを表すplistの例は[0,0,1,1]であり。
その文章化された表現presence_timetext([0,0,1,1])は" 12:00-24:00"である

plist:
これはpresence_roundoffのplistとreturnの仕様と同じ

return:
勤務状況のlistに対応するstr
```
###main.pyのリクエストハンドラ
- def slackevent(request):
```
使用しない
```
- def hello(request)
```
"/"へのリクエストに対するレスポンスを返す
データベースの内容を全部吐き出す
デバッグ用
```
def presence_adaypost(request):
``` 
"/presence_adaypost"へのリクエストに対するレスポンスを返す
SlackのAPIでチャンネルに投稿する
その日の終わり23:59にリクエストされることを想定している
```
def presence_adaymake(request):
```
"/presence_adaymake"へのリクエストに対するレスポンスを返す
データベースに当日のログイン状況を記録するためのモデルを作成する
その日の始まり0:00にリクエストされることを想定している
```
def presence_test(request):
```
"/presence_text"へのリクエストに対応するレスポンスを返す
データベース上の最新のモデルを取得し
モデル内のログイン状況を表すlistを参照し
listの現在時刻に対応する値を現在のログイン状況に変更し
データベースに上書き保存する
```
def oauthsend(request):
``` 
Slackアプリの配布のための関数
TNT内部でしか使わないので使用しない
```
def oauthrecv(request):
``` 
Slackアプリの配布のための関数
TNT内部でしか使わないので使用しない
```
## Requirement
```
Python2.7
Google Cloud SDK 245.0.0
```
## Usage
1. slackのワークスペースでアプリを作成、詳細は後述
2. main.pyのOAUTH_BOT_TOKENをアプリのボット用トークンに変更
3. アップロード >gcloud app deploy
4. slackのワークスペースでアプリユーザーを任意のチャンネルに追加
5. 毎日そのチャンネルにログイン状況が書き込まれます



## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author

[三角聡 sciphelt](https://github.com/sciphelt)