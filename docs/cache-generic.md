# cache-generic

任意のディレクトリをランナー上の永続キャッシュに restore / save する汎用 Action です。

## 種別

Node Action（node20）

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `target-dir` | ✅ | — | キャッシュ対象のディレクトリ（プロジェクトルートからの相対パス） |
| `cache-key` | ✅ | — | キャッシュキー（完全一致で検索される） |
| `restore-keys` | — | `''` | フォールバック用のキープレフィックス（カンマ区切り）。完全一致がない場合に前方一致で検索する。 |
| `skip-save` | — | `'false'` | `'true'` にするとポストステップでの自動 save をスキップする |

## 出力

なし

## 動作

- **main ステップ**: `cache.py restore` を呼び出してキャッシュを復元する
- **post ステップ**: `success()` 時のみ `cache.py save` を呼び出してキャッシュを保存する

`$PERSISTENT_CACHE_DIR` 環境変数が示す永続ディレクトリを使用します（GitHub のキャッシュストレージとは別物）。

## 使用例

### NuGet パッケージのキャッシュ

```yaml
- name: NuGet パッケージキャッシュを復元する
  uses: surface0/unity-ci-actions/actions/cache-generic@v1
  with:
    target-dir: Packages/nuget-packages/InstalledPackages
    cache-key: ${{ github.event.repository.name }}-nuget-${{ hashFiles('Packages/nuget-packages/packages.config') }}
    restore-keys: ${{ github.event.repository.name }}-nuget-
```

### セーブをスキップする場合

```yaml
- name: キャッシュを読み取り専用で復元する
  uses: surface0/unity-ci-actions/actions/cache-generic@v1
  with:
    target-dir: some/dir
    cache-key: my-cache-key
    skip-save: 'true'
```

## 注意事項

- `cache-key` が同一の場合、既存エントリを上書きして保存します。
- 古いエントリの削除は [cache-purge](cache-purge.md) で行います。
- `restore-keys` はカンマ区切りで複数指定できます。前方一致で最新エントリが選ばれます。
