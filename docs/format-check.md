# format-check

`dotnet format --verify-no-changes` を実行して C# コードのフォーマットを検証する Action です。
エラーが検出された場合、GitHub Step Summary に表形式のレポートを出力します。

## 種別

Composite Action

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `solution` | ✅ | — | ソリューションファイルのパス（例: `MyProject.sln`） |
| `include` | — | `''` | チェック対象のパス（`--include` に渡す値）。空の場合は全ファイルが対象。 |

## 出力

なし

## 動作

1. `dotnet format --verify-no-changes <solution> --report format-report.json` を実行する
2. エラーがある場合、`format-report.json` を解析して Step Summary に以下の形式でレポートを出力する

```
## Format Check Failed
フォーマットエラーが N 件 検出されました。

| File | Line | Col | Rule | Description |
|------|-----:|----:|------|-------------|
| `Assets/Scripts/Foo.cs` | 12 | 1 | `IDE0055` | Fix formatting |
```

## 使用例

### ソリューション全体をチェックする

```yaml
- name: フォーマットをチェックする
  uses: synSophia/ss-fleet-ci/actions/format-check@v1
  with:
    solution: MyProject.sln
```

### 特定ディレクトリのみチェックする

```yaml
- name: フォーマットをチェックする
  uses: synSophia/ss-fleet-ci/actions/format-check@v1
  with:
    solution: MyProject.sln
    include: Assets/Scripts/
```

### 静的解析と並べて実行する（format 失敗時も inspectcode を実行する）

```yaml
- name: フォーマットをチェックする
  id: format_check
  continue-on-error: true
  uses: synSophia/ss-fleet-ci/actions/format-check@v1
  with:
    solution: ${{ inputs.solution }}

- name: 静的解析を実行する
  uses: synSophia/ss-fleet-ci/actions/inspectcode@v1
  with:
    solution: ${{ inputs.solution }}
    github-token: ${{ secrets.github-token }}

- name: フォーマットチェックが失敗していた場合はエラーにする
  if: steps.format_check.outcome == 'failure'
  run: exit 1
  shell: bash
```

## 注意事項

- `dotnet format` は .NET SDK に含まれています。ランナーまたはコンテナに .NET SDK が必要です。
- ソリューションファイルは Unity の場合、`run-build` で Rider/VS の SyncSolution を実行して生成します。
- フォーマットの自動修正は `dotnet format <solution>` をローカルで実行してください。
