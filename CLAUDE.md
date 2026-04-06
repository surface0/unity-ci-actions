# ss-fleet-ci

社内のセルフホストランナーで Unity CI を実行するための、共有 composite action とスクリプトのリポジトリ。
`synSophia` Org 内のプロジェクトから GitHub Actions のリポジトリ参照で使用する（サブモジュールではない）。

## ディレクトリ構造

```
.github/
  workflows/              # reusable workflow（他リポジトリから uses: で呼び出す）
    build-linux.yml       # Linux ビルド
    build-windows.yml     # Windows/Switch ビルド
    test-linux.yml        # Linux テスト（EditMode / PlayMode）
    test-windows.yml      # Windows テスト（EditMode / PlayMode）
    code-quality.yml      # フォーマットチェック + 静的解析（ReSharper）
    cspell.yml            # スペルチェック
    lfs-cache-daily.yml   # Git LFS キャッシュ日次更新
    cache-cleanup.yml     # 古いキャッシュの削除
    generate-alf.yml      # Unity ALF 生成
actions/                  # GitHub Actions の composite action
  activate-unity-license/ # ULF を使ったライセンス認証
  cache-generic/          # 任意ディレクトリのキャッシュ save/restore
  cache-lfs/              # Git LFS オブジェクトのキャッシュ save/restore
  cache-library/          # Unity Library のキャッシュ save/restore
  cache-purge/            # 古いキャッシュファイルの削除
  generate-alf/           # ALF ファイル生成と artifact アップロード
  get-unity-version/      # ProjectVersion.txt からバージョン取得
  run-build/              # Unity バッチモードビルド実行
  run-tests/              # Unity バッチモードテスト実行
  setup-nintendo-sdk/     # NINTENDO_SDK_ROOT 環境変数のセット
scripts/                  # action 内から呼び出す Python スクリプト
  build.py                # Unity バッチモードビルド実行
  test.py                 # Unity バッチモードテスト実行（JUnit XML 出力）
  activate.py             # ライセンス管理（ALF 生成 / ULF 認証）
  cache.py                # キャッシュの save / restore / purge
  get_unity_version.py    # ProjectVersion.txt からバージョンを stdout に出力
  unity_utils.py          # Unity 実行ファイル検索・起動のユーティリティ
workflow-examples/        # 利用側リポジトリ向けのワークフロー記述例
```

## Org リポジトリとして参照する

ワークフローから composite action を参照する形式:

```yaml
uses: synSophia/ss-fleet-ci/actions/<action-name>@v1
```

reusable workflow を参照する形式:

```yaml
jobs:
  my-job:
    uses: synSophia/ss-fleet-ci/.github/workflows/<workflow-name>.yml@v1
    with:
      some-input: value
    secrets:
      some-secret: ${{ secrets.SOME_SECRET }}
```

### 利用側リポジトリの設定

- `ss-fleet-ci` の Settings → Actions → Access →
  **「Accessible from repositories in the 'synSophia' organization」** を有効にすること

### スクリプトのパス参照

composite action 内から Python スクリプトを参照する場合は `$GITHUB_ACTION_PATH` を使用する。
node action（`dist/main.js`）内からは `__dirname` を使用する。

```bash
# composite action 内（action.yml の run ステップ）
python "$GITHUB_ACTION_PATH/../../scripts/build.py"

# node action 内（cache-action.mjs）
join(__dirname, '..', '..', '..', 'scripts', 'cache.py')
```

## スクリプト仕様

### build.py

Unity プロジェクトをバッチモードで実行する。

```
python build.py --method <ClassName.Method> --target <BuildTarget> [--project <path>] [--dry-run]
```

- `--method`: 呼び出す C# 静的メソッド（必須）
- `--target`: ビルドターゲット（省略時: `Switch`）
- `--project`: プロジェクトパス（省略時: カレントディレクトリ）

### test.py

Unity プロジェクトの EditMode / PlayMode テストをバッチモードで実行する。
テスト結果は `com.nowsprinting.test-helper` の `-testHelperJUnitResults` オプションで JUnit XML 形式に出力される。

```
python test.py --platform <EditMode|PlayMode> --results <path> [--project <path>] [--dry-run]
```

- `--platform`: テストプラットフォーム（省略時: `EditMode`）
- `--results`: テスト結果ファイルのパス（省略時: `test-results.xml`）
- `--project`: プロジェクトパス（省略時: カレントディレクトリ）

> **注意:** `-runTests` と `-quit` を同時に指定すると Unity が終了前にテストを中断する。
> `unity_utils.run_unity` は `-runTests` が引数に含まれる場合に限り `-quit` を自動付加しない。

### activate.py

Unity ライセンス管理。サブコマンドは 2 種。

```
python activate.py generate-alf [--project <path>]
python activate.py activate --license-file <path-to-ulf> [--project <path>]
```

### cache.py

ディレクトリを `.tar.zst` 形式で圧縮してキャッシュする。`--cache-dir` または環境変数 `PERSISTENT_CACHE_DIR` でキャッシュ保存先を指定する。

```
python cache.py --cache-dir <dir> save    --target-dir <dir> --cache-key <key>
python cache.py --cache-dir <dir> restore --target-dir <dir> --cache-key <key> [--restore-keys <key1,key2>]
python cache.py --cache-dir <dir> purge   [--days <n>]
```

- `save` は一時ファイルに書き込んでから `os.replace` でアトミックにリネームする（同時アクセス対策）
- `restore` はプライマリキーが見つからない場合、`--restore-keys` のプレフィックス一致で最新ファイルにフォールバックする
- `purge` は指定日数より古いキャッシュファイルを削除する（デフォルト 14 日）

### get_unity_version.py

```
python get_unity_version.py [--project <path>]
```

`ProjectSettings/ProjectVersion.txt` からバージョン文字列を読み取り stdout に出力する。ワークフローの `steps output` へ渡す用途を想定。

## node action のビルド

`cache-generic` / `cache-lfs` / `cache-library` は rollup でバンドルしている。ソース変更後は必ずリビルドしてコミットすること。

```bash
npm install
npm run build
```

## セルフホストランナーの要件

### 必須ツール

| ツール | 用途 |
|---|---|
| Python 3.12+ | スクリプト実行 |
| `zstandard` (pip) | cache.py でのキャッシュ圧縮 |
| Git + Git Bash | bash シェルが必要なステップで使用 |
| Unity Hub + Unity Editor | ビルド・ライセンス認証 |

### 必須環境変数（ランナー側で設定）

| 変数名 | 内容 | 例 |
|---|---|---|
| `PERSISTENT_CACHE_DIR` | Library などのキャッシュ保存先 | `C:\ActionsRunnerCache` |
| `LFS_CACHE_DIR` | Git LFS オブジェクトのキャッシュ保存先 | `C:\GitLFSCaches` |

### Windows ランナー固有の設定

- パス長 260 文字制限の解除が必要:
  ```
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
  ```
- セキュリティソフト（ESET 等）のリアルタイムスキャンから Unity のビルドキャッシュディレクトリを除外する
- Git のスクリプト実行ポリシーの確認: `Get-ExecutionPolicy -List`

### Unity ライセンスの準備

1. `generate-alf` action または `activate.py generate-alf` で ALF ファイルを生成
2. [https://license.unity3d.com/manual](https://license.unity3d.com/manual) でシリアルキーを入力して ULF を取得
3. ULF ファイルを GitHub Secret（`UNITY_LICENSE_LINUX` / `UNITY_LICENSE_WINDOWS`）に格納する

## このファイルのメンテナンス

ディレクトリ構造・参照形式・規約に変更が生じた場合は、このファイルを同時に更新すること。
Claude がリポジトリを変更する際も、CLAUDE.md の記述が実態と乖離する場合は自動的に更新する。

## action 作成・改修の規約

### 名前とコメントの方針

- `name` および `description` は日本語で記述する
- ステップ名（`- name:`）も日本語で記述する
- 以下に該当する箇所にはインラインコメントを付ける:
  - ランナー側の設定（環境変数など）に依存している箇所
  - フォールバック・条件分岐の意図が自明でない箇所
  - プラットフォーム固有の処理（`cygpath` など Windows 対応）
  - `if: always()` など、エラー時の挙動に影響するフラグ

### cygpath について

Windows の Git Bash 環境では POSIX パスと Windows パスの変換に `cygpath` を使用する。
Linux ランナーには存在しないため、`command -v cygpath` で存在チェックを行うパターンを統一して使用する。

```bash
if command -v cygpath > /dev/null 2>&1; then
  script_path=$(cygpath -u "$GITHUB_ACTION_PATH/../../scripts/script.py")
else
  script_path="$GITHUB_ACTION_PATH/../../scripts/script.py"
fi
python "$script_path"
```
