# run-tests

`scripts/test.py` を通じて Unity をバッチモードで起動し、Unity Test Runner でテストを実行する Action です。

## 種別

Composite Action

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `platform` | — | `'EditMode'` | テストプラットフォーム（`EditMode` または `PlayMode`） |
| `results` | — | `'test-results.xml'` | テスト結果ファイルのパス（JUnit XML 形式） |

## 出力

なし（テスト結果は `results` で指定したパスに JUnit XML 形式で出力される）

## 動作

`scripts/test.py --platform <platform> --results <results>` を実行します。
Windows（Git Bash）環境では `cygpath` によるパス変換を自動で行います。

## 使用例

### EditMode テストを実行する

```yaml
- name: Unity テストを実行する
  uses: surface0/unity-ci-actions/actions/run-tests@v1
  with:
    platform: EditMode
    results: test-results.xml
```

### テスト結果を artifact にアップロードする

```yaml
- name: Unity テストを実行する
  uses: surface0/unity-ci-actions/actions/run-tests@v1
  with:
    platform: EditMode
    results: test-results.xml

- name: テスト結果をアップロードする
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.xml
```

### PlayMode テストを実行する

```yaml
- name: PlayMode テストを実行する
  uses: surface0/unity-ci-actions/actions/run-tests@v1
  with:
    platform: PlayMode
    results: playmode-results.xml
```

## 注意事項

- Unity ライセンスの認証（[activate-unity-license](activate-unity-license.md)）を事前に行う必要があります。
- テスト結果の集計・可視化は別途 `actions/upload-artifact` などで行ってください。
- Switch 実機テストには対応していません（EditMode / PlayMode はエディタ上で実行されます）。
