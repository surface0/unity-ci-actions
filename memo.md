# Unity用ランナーセットアップ

## 環境変数設定

| 変数名 | 内容 | 例 |
| --- | --- | --- |
| UNITY_LICENSE_DIR | バージョンごとのULFファイルを置くパス | C:\UnityLicenses |
| PERSISTENT_CACHE_DIR | Libraryなどのキャッシュを保存しておくパス | C:\ActionsRunnerCache |
| LFS_CACHE_DIR | Git LFSのオブジェクトデータをキャッシュしておくパス | C:\GitLFSCaches |

## NintendoSDKとUnityのインストール

- 必要なNintendoSDKとUnityを普通にインストールする


## ULFファイルの作成

- UnityLicenseフォルダを作成する
- UnityバージョンごとにALFファイルを作成し、Switchのシリアルコードを使用してULFファイルを取得する
- ULFファイルを `Unity_vXXXX.X.X.ulf`（ex. Unity_v6000.3.4f1.ulf）として保存する


## スクリプト実行ポリシーの変更

```
Get-ExecutionPolicy -List
```

## Git bashインストール

bashを使えるようにする為。
普通にgit入れる。
Git/binにパスを通す。

## Pythonとライブラリのインストール

Pythonは全ユーザーインストールする。

```
pip install zstandard
```

もしかしたらいらんかも
CLI版をインストールする
グローバルインストールすると、エイリアスになってランナーから使えないので手動配置が好ましい。

## パス260文字制限解除

```
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

## ESETの除外

リアルタイムスキャンを除外
