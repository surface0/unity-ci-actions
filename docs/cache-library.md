# cache-library

Unity の `Library` ディレクトリをランナー上の永続キャッシュに restore / save する Action です。
キャッシュキーは Unity バージョンとブランチ名を組み合わせて自動生成されます。

## 種別

Node Action（node20）

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `unity-version` | ✅ | — | Unity バージョン文字列（例: `6000.3.4f1`）。[get-unity-version](get-unity-version.md) の出力を渡す。 |
| `skip-save` | — | `'false'` | `'true'` にするとポストステップでの自動 save をスキップする |

## 出力

なし

## 動作

- キャッシュキーは `<repo>-library-<unity-version>-<branch>` の形式で自動生成される
- **main ステップ**: `Library` ディレクトリをキャッシュから復元する
- **post ステップ**: `success()` 時のみキャッシュを保存する

## 使用例

```yaml
- name: Unity バージョンを取得する
  id: get_unity_version
  uses: synSophia/ss-fleet-ci/actions/get-unity-version@v1

- name: Unity Library キャッシュを復元する
  uses: synSophia/ss-fleet-ci/actions/cache-library@v1
  with:
    unity-version: ${{ steps.get_unity_version.outputs.unity-version }}
```

## 注意事項

- `unity-version` の値によってキャッシュキーが変わるため、Unity バージョンを変更した際は古いキャッシュが自動的に無視されます。
- ブランチごとにキャッシュが分離されるため、`main` ブランチと feature ブランチで別々のキャッシュが維持されます。
- 古いキャッシュの削除は [cache-purge](cache-purge.md) で行います。
