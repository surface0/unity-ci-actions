# inspectcode

JetBrains ReSharper CLI（`inspectcode`）で C# の静的解析を実行し、
`reviewdog` を使って結果を GitHub Checks に報告する Action です。

## 種別

Composite Action

## 入力

| パラメータ | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `solution` | ✅ | — | ソリューションファイルのパス（例: `MyProject.sln`） |
| `include` | — | `''` | 解析対象のパス（`--include` に渡す値）。空の場合は全ファイルが対象。 |
| `github-token` | ✅ | — | GitHub Token（reviewdog の GitHub Checks 書き込みに使用） |

## 出力

なし（結果は GitHub Checks の "ReSharper Inspections" として報告される）

## 動作

1. `/tmp` に JetBrains ReSharper CLI (`jb`) をインストールする
2. `jb inspectcode <solution> --output=inspectcode-report.sarif --format=Sarif` を実行する
3. `reviewdog/action-setup@v1` で reviewdog をセットアップする
4. SARIF レポートを reviewdog に渡し、`github-check` reporter でレポートを投稿する（エラー時は失敗）

## 必要な権限

ジョブに以下のパーミッションが必要です。

```yaml
permissions:
  checks: write
  contents: read
```

## 使用例

```yaml
- name: 静的解析を実行する
  uses: surface0/unity-ci-actions/actions/inspectcode@v1
  with:
    solution: MyProject.sln
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

### 特定ディレクトリのみ解析する

```yaml
- name: 静的解析を実行する
  uses: surface0/unity-ci-actions/actions/inspectcode@v1
  with:
    solution: MyProject.sln
    include: Assets/Scripts/
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

## 注意事項

- ソリューションファイルは Unity の場合、`run-build` で Rider/VS の SyncSolution を実行して生成します。
- JetBrains CLI は `/tmp/jetbrains-tools` にインストールされます。ワークスペースを汚しません。
- 解析には時間がかかります（プロジェクト規模によっては数分）。
- `github-token` には `GITHUB_TOKEN` を使用できますが、fork PR からのトリガーでは `checks: write` が制限される場合があります。
