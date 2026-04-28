# run-build

`scripts/build.py` を通じて Unity をバッチモードで起動し、指定した C# 静的メソッドを実行する Action です。
ビルドのほか、ソリューション生成など Unity のバッチ処理全般に使用できます。

## 種別

Composite Action

## 入力

| パラメータ | 必須 | 説明 |
|-----------|:----:|------|
| `method` | ✅ | 呼び出す C# 静的メソッドの完全修飾名（例: `BuildScript.Build`） |
| `target` | ✅ | ビルドターゲット（例: `Switch`, `StandaloneLinux64`） |

## 出力

なし

## 動作

`scripts/build.py --method <method> --target <target>` を実行します。
Unity がバッチモードで起動し、指定メソッドを実行します。

## 使用例

### Switch ビルド

```yaml
- name: Unity ビルドを実行する
  uses: surface0/unity-ci-actions/actions/run-build@v1
  with:
    method: BuildScript.Build
    target: Switch
```

### ソリューションファイルの生成（コード品質チェックの前処理）

```yaml
- name: ソリューションファイルを生成する
  uses: surface0/unity-ci-actions/actions/run-build@v1
  with:
    method: Packages.Rider.Editor.RiderScriptEditor.SyncSolution
    target: StandaloneLinux64
```

### Linux ビルド

```yaml
- name: Unity ビルドを実行する
  uses: surface0/unity-ci-actions/actions/run-build@v1
  with:
    method: BuildScript.BuildLinux
    target: StandaloneLinux64
```

## 注意事項

- `method` に指定するクラス・メソッドはプロジェクトの `Assets/Editor/` 以下に実装する必要があります。
- Unity ライセンスの認証（[activate-unity-license](activate-unity-license.md)）を事前に行う必要があります。
- Switch ビルドの場合は Nintendo SDK のセットアップ（[setup-nintendo-sdk](setup-nintendo-sdk.md)）も必要です。
