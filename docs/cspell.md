# cspell

`cspell lint` を実行してスペルチェックを行う Action です。
エラーが検出された場合、GitHub Step Summary に表形式のレポートを出力します。

## 種別

Composite Action

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `config` | — | `'cspell.json'` | cspell 設定ファイルのパス |

## 出力

なし

## 動作

1. `npx cspell lint --config <config> --no-progress` を実行する
2. エラーがある場合、Step Summary に以下の形式でレポートを出力して `exit 1` する

```
## Spell Check Failed
スペルエラーが N 件 検出されました。

| File | Line | Col | Word |
|------|-----:|----:|------|
| `path/to/file.cs` | 10 | 5 | `somword` |
```

## 使用例

### デフォルト設定ファイルを使用する場合

```yaml
- name: CSpell を実行する
  uses: surface0/unity-ci-actions/actions/cspell@v1
```

### 設定ファイルのパスを指定する場合

```yaml
- name: CSpell を実行する
  uses: surface0/unity-ci-actions/actions/cspell@v1
  with:
    config: .cspell/cspell.json
```

## プロジェクト固有単語の追加

`cspell.json` の `words` または専用の単語リストファイル（例: `.cspell/project-words.txt`）に追加します。

```json
{
  "version": "0.2",
  "words": ["MyCustomWord"],
  "dictionaries": ["project-words"],
  "dictionaryDefinitions": [
    { "name": "project-words", "path": ".cspell/project-words.txt", "addWords": true }
  ]
}
```

## 注意事項

- Node.js が利用可能な環境で実行してください（`npx` を使用します）。
- `ubuntu-latest` ランナーでは追加インストール不要です。
