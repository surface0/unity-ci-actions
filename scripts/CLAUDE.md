# 目標

- CLIでUnityビルドやテストが実行できるようにします。
- GitHub ActionsのCIでWindowsセルフホストランナーで実行できるようにする想定です。
- ビルドターゲットはSwitchです。
- ビルド環境のプラットフォームはWindowsを想定し、CI用のスクリプトはPythonで記述します。
- Unityバージョン/GitブランチごとにLibraryキャッシュを作成して再利用するようにします。
- ライセンスアクティベーションはULFファイルを用いてCLIで実行します。

# 進捗

- `scripts/build.py` を作成しました。
  - サブコマンドで `build`, `test`, `activate` を実行できます。
    - `build`: 指定したメソッドを実行してビルドします。
    - `test`: ユニットテストを実行します。
    - `activate`: ULFファイルを使ってライセンスを認証します。
      - `--license-file` オプションを追加し、ULFファイルを直接指定できるようになりました。
      - `--license-file` が指定されない場合、デフォルトのディレクトリ `C:\UnityLicenses` から、プロジェクトのUnityバージョンに合致するULFファイル（例: `Unity_v{バージョン}.ulf`）を検索して使用するフォールバック機能が実装されました。
      - `find_unity_exe` 関数が、Unityの実行ファイルパスに加えて特定したUnityのバージョン文字列も返すようになり、`activate` コマンドがバージョン指定なしでも適切なライセンスファイルを検索できるよう改善されました。
  - プロジェクトの `ProjectVersion.txt` からUnityバージョンを自動で判別し、Unity Hubのインストール先から適切なUnity実行ファイルを探します。
- **キャッシュ機能の追加 (完了)**:
  - キャッシュ機能は `scripts/cache.py` に切り出されました。
  - `cache.py` は以下の機能を持ちます。
    - `save` コマンド: Unity Library などのキャッシュを `.tar.zst` 形式で保存します。
    - `restore` コマンド: `.tar.zst` 形式のキャッシュを復元します。
  - キャッシュディレクトリは `--cache-dir` 引数、または環境変数 `PERSISTENT_CACHE_DIR` で指定します。
  - キャッシュキーはUnityバージョンとGitブランチ名を組み合わせて生成されます。
  - 圧縮形式は `tar.zst` を使用し、Pythonの `tarfile` および `zstandard` ライブラリを利用します。`zstandard` ライブラリは既にグローバルにインストール済みです。
  - `scripts/build.py` からはキャッシュ操作に関するコードは完全に削除され、`cache.py` はワークフローから直接呼び出す独立したスクリプトとして機能します。
  - **補足事項**:
    - `zstandard` ライブラリはグローバルにインストール済みのため、ワークフローでの`pip install`は不要です。
    - キャッシュの保存は、ビルドが成功した場合にのみ実行します。
    - `PERSISTENT_CACHE_DIR` はランナーに依存するため、ワークフローファイル内では定義せず、ランナー側の環境変数として設定されていることを前提とします。
  - **get_unity_version.py の作成**:
    - `scripts/get_unity_version.py` を新規作成し、`ProjectVersion.txt` からUnityバージョンを読み取り、標準出力に出力するようにしました。
  - **cache.py の変更**:
    - キャッシュキーはワークフロー側で生成し、`--cache-key <key>` 引数として渡すように変更しました。
    - キャッシュ対象ディレクトリは `--target-dir <dir>` 引数として渡すように変更しました。
    - キャッシュキー生成の内部ロジックは削除され、外部から受け取ったキーを使用します。