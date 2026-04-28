# setup-nintendo-sdk

`NINTENDO_ROOT` と `NX_ADDON_NAME` から Nintendo SDK のパスを組み立てて
`NINTENDO_SDK_ROOT` 環境変数に設定する Action です。

## 種別

Composite Action

## 入力

なし（ランナーまたはワークフローの `env` で環境変数を設定する）

## 前提となる環境変数

| 環境変数 | 説明 |
|---------|------|
| `NINTENDO_ROOT` | Nintendo SDK のインストールルートディレクトリ（例: `D:\Nintendo`） |
| `NX_ADDON_NAME` | NX Addon のディレクトリ名（例: `NintendoSDKAddon-NX-1.0.0`） |

## 出力

| 環境変数 | 説明 |
|---------|------|
| `NINTENDO_SDK_ROOT` | `<NINTENDO_ROOT>/<NX_ADDON_NAME>/NintendoSDK` として設定される |

## 動作

`NINTENDO_ROOT` と `NX_ADDON_NAME` の両方が設定されている場合のみ `NINTENDO_SDK_ROOT` を設定します。
どちらかが未設定の場合はスキップします（Switch 以外のビルドジョブでも安全に使用できます）。

## 使用例

### ワークフロー側で環境変数を設定する

```yaml
jobs:
  build:
    runs-on: [self-hosted, Windows, Unity]
    env:
      NX_ADDON_NAME: ${{ inputs.nx-addon-name }}
    steps:
      - name: Nintendo SDK をセットアップする
        uses: surface0/unity-ci-actions/actions/nintendo-switch/setup-nintendo-sdk@v1

      - name: Unity ビルドを実行する
        uses: surface0/unity-ci-actions/actions/run-build@v1
        with:
          method: BuildScript.Build
          target: Switch
```

### `NINTENDO_ROOT` の設定場所

`NINTENDO_ROOT` はセルフホストランナーのシステム環境変数として設定することを推奨します。
各ランナーマシンの Nintendo SDK インストールパスに合わせて設定してください。

## 注意事項

- この Action は Switch ビルド専用のランナーで使用することを想定しています。
- `NINTENDO_SDK_ROOT` は Unity の Build Settings で Nintendo Switch プラットフォームを選択した際に参照されます。
- Nintendo SDK のライセンス要件に従い、SDK ファイルはリポジトリに含めないでください。
