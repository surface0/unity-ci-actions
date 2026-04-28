# cache-purge

指定日数より古い永続キャッシュファイルを削除する Action です。

## 種別

Composite Action

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `days` | — | `'14'` | この日数より古いキャッシュファイルを削除する |

## 出力

なし

## 動作

`scripts/cache.py purge --days <days>` を実行し、`$PERSISTENT_CACHE_DIR` 内の古いエントリを削除します。

## 使用例

```yaml
- name: 古いキャッシュを削除する
  uses: surface0/unity-ci-actions/actions/cache-purge@v1
  with:
    days: '14'
```

## 推奨運用

定期実行ワークフロー（`cache-cleanup.yml`）から呼び出すことを推奨します。

```yaml
# .github/workflows/cache-cleanup.yml（呼び出し側の例）
on:
  schedule:
    - cron: '0 3 * * 0'  # 毎週日曜 3:00 UTC
  workflow_dispatch:

jobs:
  cleanup:
    uses: surface0/unity-ci-actions/.github/workflows/cache-cleanup.yml@v1
```

## 注意事項

- `$PERSISTENT_CACHE_DIR` 環境変数がランナーに設定されている必要があります。
- 削除は取り消せません。`days` の値は余裕を持って設定してください。
