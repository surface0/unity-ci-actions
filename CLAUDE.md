# ss-fleet-ci

社内のセルフホストランナーで Unity CI を実行するための、共有 composite action とスクリプトのリポジトリ。
別プロジェクトから `.github/ss-fleet-ci` としてサブモジュールで組み込んで使用する。

## ディレクトリ構造

```
actions/                  # GitHub Actions の composite action
  activate-unity-license/ # ULF を使ったライセンス認証
  cache-generic/          # 任意ディレクトリのキャッシュ save/restore
  cache-lfs/              # Git LFS オブジェクトのキャッシュ save/restore
  cache-library/          # Unity Library のキャッシュ save/restore
  generate-alf/           # ALF ファイル生成と artifact アップロード
  get-unity-version/      # ProjectVersion.txt からバージョン取得
  setup-nintendo-sdk/     # NINTENDO_SDK_ROOT 環境変数のセット
scripts/                  # CI から直接呼び出す Python スクリプト
  build.py                # Unity バッチモードビルド実行
  activate.py             # ライセンス管理（ALF 生成 / ULF 認証）
  cache.py                # キャッシュの save / restore / purge
  get_unity_version.py    # ProjectVersion.txt からバージョンを stdout に出力
  unity_utils.py          # Unity 実行ファイル検索・起動のユーティリティ
workflow-examples/        # 各 action の使用例となるサンプルワークフロー
```

## サブモジュールとして組み込む

```bash
git submodule add git@github.com:synSophia/ss-fleet-ci.git .github/ss-fleet-ci
```

checkout 時にサブモジュールを含めて取得するには:

```bash
git clone --recurse-submodules <repo-url>
# または既存クローン後
git submodule update --init
```

ワークフローからのパス参照は以下のプレフィックスで統一する:

```yaml
uses: ./.github/ss-fleet-ci/actions/<action-name>  # composite action
run: python .github/ss-fleet-ci/scripts/<script>.py # スクリプト直接呼び出し
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

- `restore` はプライマリキーが見つからない場合、`--restore-keys` のプレフィックス一致で最新ファイルにフォールバックする
- `purge` は指定日数より古いキャッシュファイルを削除する（デフォルト 14 日）

### get_unity_version.py

```
python get_unity_version.py [--project <path>]
```

`ProjectSettings/ProjectVersion.txt` からバージョン文字列を読み取り stdout に出力する。ワークフローの `steps output` へ渡す用途を想定。

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
