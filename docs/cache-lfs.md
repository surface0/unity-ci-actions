# cache-lfs

Git LFS オブジェクト（`.git/lfs`）をランナー上の永続キャッシュに restore / save する Action です。

## 種別

Node Action（node20）

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `cache-key` | ✅ | — | キャッシュキー |
| `skip-save` | — | `'false'` | `'true'` にするとポストステップでの自動 save をスキップする |

## 出力

なし

## 動作

- **main ステップ**: `.git/lfs` ディレクトリをキャッシュから復元する
- **post ステップ**: `success()` 時のみキャッシュを保存する

## 推奨構成

LFS オブジェクトの全件ダウンロードを避けるため、以下の順序で使用します。

```yaml
- name: リポジトリをチェックアウトする
  uses: actions/checkout@v6
  # lfs: true は指定しない

- name: Git LFS をインストールする
  run: git lfs install
  shell: bash

- name: Git LFS キャッシュを復元する
  uses: surface0/unity-ci-actions/actions/cache-lfs@v1
  with:
    cache-key: ${{ github.event.repository.name }}-lfs
    skip-save: 'true'   # セーブは lfs-cache-daily.yml のみで行う

- name: Git LFS オブジェクトを差分取得する
  run: git lfs pull     # キャッシュにない差分だけ取得される
  shell: bash
```

## 注意事項

- LFS キャッシュのセーブは `lfs-cache-daily.yml` ワークフローでのみ行うことを推奨します。
  ビルドジョブごとにセーブすると競合が発生する可能性があるため、通常のビルドでは `skip-save: 'true'` を指定してください。
- キャッシュ復元後に `git lfs pull` を実行することで、差分オブジェクトのみをダウンロードします。
