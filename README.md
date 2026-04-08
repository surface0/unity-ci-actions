# ss-fleet-ci

シンソフィア社内の開発支援サーバー群 **SS Fleet** のセルフホストランナーで Unity CI を実行するための、共有 composite actions と reusable workflows のリポジトリ。

`synSophia` Org 内のプロジェクトから GitHub Actions のリポジトリ参照で使用する（サブモジュールではない）。

## Actions 一覧

詳細は [docs/](docs/) を参照。

| Action | 概要 |
|--------|------|
| [activate-unity-license](docs/activate-unity-license.md) | ULF ファイルを使って Unity ライセンスを認証する |
| [cache-generic](docs/cache-generic.md) | 任意のディレクトリを永続キャッシュで restore / save する |
| [cache-lfs](docs/cache-lfs.md) | Git LFS オブジェクトを永続キャッシュで restore / save する |
| [cache-library](docs/cache-library.md) | Unity Library ディレクトリを永続キャッシュで restore / save する |
| [cache-purge](docs/cache-purge.md) | 古い永続キャッシュファイルを削除する |
| [cspell](docs/cspell.md) | CSpell によるスペルチェックを実行する |
| [format-check](docs/format-check.md) | `dotnet format` による C# フォーマットチェックを実行する |
| [generate-alf](docs/generate-alf.md) | Unity 手動アクティベーション用の ALF ファイルを生成する |
| [get-unity-version](docs/get-unity-version.md) | `ProjectVersion.txt` から Unity バージョンを取得する |
| [inspectcode](docs/inspectcode.md) | ReSharper + reviewdog による C# 静的解析を実行する |
| [run-build](docs/run-build.md) | Unity バッチモードでビルドを実行する |
| [run-tests](docs/run-tests.md) | Unity バッチモードでテストを実行する |
| [setup-nintendo-sdk](docs/setup-nintendo-sdk.md) | `NINTENDO_SDK_ROOT` 環境変数を設定する |

## Reusable Workflows 一覧

ワークフロー例は [workflow-examples/](workflow-examples/) を参照。

| ワークフロー | 概要 |
|---|---|
| `build-linux.yml` | Linux ランナーで Unity ビルドを実行する |
| `build-windows.yml` | Windows ランナーで Unity / Nintendo Switch ビルドを実行する |
| `test-linux.yml` | Linux ランナーで Unity テスト（EditMode / PlayMode）を実行する |
| `test-windows.yml` | Windows ランナーで Unity テスト（EditMode / PlayMode）を実行する |
| `code-quality.yml` | C# フォーマットチェック（`dotnet format`）と静的解析（ReSharper）を実行する |
| `cspell.yml` | スペルチェックを実行する |
| `lfs-cache-daily.yml` | Git LFS キャッシュを日次で更新する |
| `cache-cleanup.yml` | 古いキャッシュを削除する |
| `generate-alf.yml` | Unity ALF ファイルを生成して artifact にアップロードする |

## 参照形式

```yaml
# composite action
uses: synSophia/ss-fleet-ci/actions/<action-name>@v1

# reusable workflow
jobs:
  my-job:
    uses: synSophia/ss-fleet-ci/.github/workflows/<workflow-name>.yml@v1
    with:
      some-input: value
    secrets:
      some-secret: ${{ secrets.SOME_SECRET }}
```

## セルフホストランナーの要件

### 共通（Linux / Windows）

**Python のセットアップ**

多くの action が内部で Python スクリプトを使用する。Python はランナーへの事前インストール不要で、このリポジトリの reusable workflow はすべて最初のステップで `actions/setup-python` を実行する。

composite action を直接呼び出す場合は、呼び出し側ワークフローで Python をセットアップすること。

```yaml
- name: Python をセットアップする
  uses: actions/setup-python@v5
  with:
    python-version: '3.14'
```

**環境変数**

以下の環境変数をランナー側で設定すること。

| 変数名 | 必須 | 内容 |
|---|---|---|
| `PERSISTENT_CACHE_DIR` | 必須 | Library などのキャッシュ保存先（例: `C:\ActionsRunnerCache`） |
| `LFS_CACHE_DIR` | 任意 | Git LFS オブジェクトのキャッシュ保存先。未設定時は `PERSISTENT_CACHE_DIR` にフォールバックする |

### Linux ランナー

Linux ワークフローはジョブコンテナ内で実行されるため、以下は**コンテナイメージ側**の要件となる。

| ツール | 用途 |
|---|---|
| Git + Git LFS | ソース取得・LFS オブジェクト取得 |
| Unity Hub + Unity Editor | ビルド・テスト・ライセンス認証 |

ランナー側では、永続キャッシュディレクトリ（`/var/actions-runner-persistent-caches`）をコンテナにマウントするよう設定すること。

### Windows ランナー

Windows ワークフローはランナー上で直接実行される。

| ツール | 用途 |
|---|---|
| Git + Git Bash | bash シェルが必要なステップで使用 |
| Unity Hub + Unity Editor | ビルド・テスト・ライセンス認証 |

また、以下の設定が必要となる。

- ランナーサービスのアカウントをローカルシステムアカウント（`NT AUTHORITY\SYSTEM`）に設定する
- パス長 260 文字制限を解除する:
  ```
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
  ```
- セキュリティソフトのリアルタイムスキャンから Unity のビルドキャッシュディレクトリを除外する

### Unity ライセンスの準備

1. `generate-alf` action または `generate-alf.yml` workflow で ALF ファイルを生成する
2. [Unity Manual Activation](https://license.unity3d.com/manual) でシリアルキーを入力して ULF を取得する
3. ULF ファイルを GitHub Secret（`UNITY_LICENSE_LINUX` / `UNITY_LICENSE_WINDOWS`）に格納する

## 開発者向け

### node action のビルド

`cache-generic` / `cache-lfs` / `cache-library` は rollup でバンドルしている。ソース変更後は必ずリビルドしてコミットすること。

```bash
npm install
npm run build
```

### ドキュメントの更新

action や workflow を追加・変更した場合は `docs/` 以下の対応するファイルを同時に更新すること。
