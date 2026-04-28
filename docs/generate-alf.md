# generate-alf

Unity の手動アクティベーション用 ALF ファイルを生成し、GitHub Actions の artifact としてアップロードする Action です。

## 種別

Composite Action

## 入力

なし

## 出力

なし（ALF ファイルは `unity-activation-file` という名前の artifact としてアップロードされる）

## 動作

1. `scripts/activate.py generate-alf` を実行して `*.alf` ファイルを生成する
2. `actions/upload-artifact@v4` で artifact にアップロードする
3. ログに手動アクティベーションの手順を表示する

## 使用例

```yaml
jobs:
  generate-alf:
    runs-on: [self-hosted, Windows, Unity]
    steps:
      - uses: actions/checkout@v6

      - name: ALF ファイルを生成する
        uses: surface0/unity-ci-actions/actions/generate-alf@v1
```

## 手動アクティベーション手順

1. このワークフローの成果物 `unity-activation-file` をダウンロードする
2. [https://license.unity3d.com/manual](https://license.unity3d.com/manual) にアクセスする
3. Unity アカウントでサインインする
4. ダウンロードした `.alf` ファイルをアップロードする
5. シリアルキーを入力してアクティベーションを完了する
6. 生成された `.ulf` ファイルをダウンロードする
7. `.ulf` ファイルの内容を GitHub Secret（例: `UNITY_LICENSE`）に設定する

その後は [activate-unity-license](activate-unity-license.md) を使って CI から認証できます。

## 注意事項

- この Action は初回セットアップ時にのみ使用します。通常のビルドには不要です。
- Unity のバージョンを大きく変更した場合、ALF の再生成が必要になることがあります。
