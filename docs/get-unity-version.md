# get-unity-version

`ProjectSettings/ProjectVersion.txt` から Unity バージョン文字列を読み取り、ステップ出力に設定する Action です。

## 種別

Composite Action

## 入力

なし

## 出力

| 出力名 | 説明 | 例 |
|--------|------|----|
| `unity-version` | Unity バージョン文字列 | `6000.3.4f1` |

## 動作

`scripts/get_unity_version.py` を実行して `ProjectVersion.txt` からバージョンを読み取り、
`$GITHUB_OUTPUT` に `version=<value>` を書き出します。

Windows（Git Bash）環境では `cygpath` によるパス変換を自動で行います。

## 使用例

```yaml
- name: Unity バージョンを取得する
  id: get_unity_version
  uses: synSophia/ss-fleet-ci/actions/get-unity-version@v1

# 後続ステップで参照する
- name: Unity Library キャッシュを復元する
  uses: synSophia/ss-fleet-ci/actions/cache-library@v1
  with:
    unity-version: ${{ steps.get_unity_version.outputs.unity-version }}
```

## 注意事項

- リポジトリがチェックアウト済みであることが前提です（`actions/checkout@v4` を先に実行する）。
- `ProjectSettings/ProjectVersion.txt` が存在しない場合はエラーになります。
