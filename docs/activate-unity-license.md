# activate-unity-license

Unity ライセンスファイル（ULF）の内容を Secret から受け取り、ランナー上で Unity ライセンスを認証します。

## 種別

Composite Action

## 入力

| パラメータ | 必須 | 説明 |
|-----------|:----:|------|
| `license-content` | ✅ | Unity ライセンスファイル（.ulf）の内容。GitHub Secret として管理する。 |

## 出力

なし

## 動作

1. `license-content` の内容を `/tmp/unity_license.ulf` に書き出す
2. `scripts/activate.py activate` を実行してライセンスを認証する
3. `always()` 条件で `/tmp/unity_license.ulf` を削除する（認証失敗時も削除される）

Windows（Git Bash）環境では `cygpath` によるパス変換を自動で行います。

## 使用例

```yaml
- name: Unity ライセンスを認証する
  uses: surface0/unity-ci-actions/actions/activate-unity-license@v1
  with:
    license-content: ${{ secrets.UNITY_LICENSE }}
```

## 注意事項

- ULF ファイルの内容は GitHub Secret に格納し、ワークフロー内にハードコードしないこと。
- 認証後は必ず Unity をアクティベーション解除してからランナーを破棄すること（セルフホストランナーの場合）。
- ALF ファイルの生成（手動アクティベーションの初回手順）は [generate-alf](generate-alf.md) を使用する。
