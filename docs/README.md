# Unity CI Actions ドキュメント

Composite Action / Node Action の一覧です。

## Actions 一覧

| Action | 概要 |
|--------|------|
| [activate-unity-license](activate-unity-license.md) | ULF ファイルを使って Unity ライセンスを認証する |
| [cache-generic](cache-generic.md) | 任意のディレクトリを永続キャッシュで restore / save する |
| [cache-lfs](cache-lfs.md) | Git LFS オブジェクトを永続キャッシュで restore / save する |
| [cache-library](cache-library.md) | Unity Library ディレクトリを永続キャッシュで restore / save する |
| [cache-purge](cache-purge.md) | 古い永続キャッシュファイルを削除する |
| [cspell](cspell.md) | CSpell によるスペルチェックを実行する |
| [format-check](format-check.md) | `dotnet format` による C# フォーマットチェックを実行する |
| [generate-alf](generate-alf.md) | Unity 手動アクティベーション用の ALF ファイルを生成する |
| [get-unity-version](get-unity-version.md) | `ProjectVersion.txt` から Unity バージョンを取得する |
| [inspectcode](inspectcode.md) | ReSharper + reviewdog による C# 静的解析を実行する |
| [run-build](run-build.md) | Unity バッチモードでビルドを実行する |
| [run-tests](run-tests.md) | Unity バッチモードでテストを実行する |
| [setup-nintendo-sdk](nintendo-switch/setup-nintendo-sdk.md) | `NINTENDO_SDK_ROOT` 環境変数を設定する |

## 参照方法

全ての Action は以下の形式で参照します。

```yaml
uses: surface0/unity-ci-actions/actions/<action-name>@v1
```

## キャッシュ設計

`cache-generic` / `cache-lfs` / `cache-library` はランナー上の永続ディレクトリ
（`$PERSISTENT_CACHE_DIR`）を使用するカスタムキャッシュ実装です。
`actions/cache` とは異なり GitHub のキャッシュストレージ容量を消費しません。

- **restore**: ジョブ開始時に自動実行
- **save**: ジョブ成功時にポストステップで自動実行（`post-if: success()`）
- **purge**: `cache-purge` action または `cache-cleanup` ワークフローで古いエントリを削除
