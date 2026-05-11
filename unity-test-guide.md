Unityテスト ガイド

## 目次

1. [🎯 目的・ポリシー](#目的ポリシー)
2. [📖 概要](#概要)
3. [📦 必要パッケージ](#必要パッケージ)
4. [🔧 アセンブリ定義（.asmdef）](#アセンブリ定義asmdef)
5. [📁 ファイル配置](#ファイル配置)
6. [🔀 テストの種類と使い分け](#テストの種類と使い分け)
7. [🏗️ 基本構造・ライフサイクル](#基本構造ライフサイクル)
8. [✅ アサーション](#アサーション)
9. [🔢 パラメータ化テスト](#パラメータ化テスト)
10. [🚫 テストの除外（Explicit / Ignore）](#テストの除外explicit--ignore)
11. [🎭 テストダブル（NSubstitute）](#テストダブルnsubstitute)
12. [⏳ 非同期テスト（UniTask）](#非同期テストunitask)
13. [▶️ PlayModeテスト固有のトピック](#playmodeテスト固有のトピック)
14. [💉 VContainerとの組み合わせ](#vcontainerとの組み合わせ)
15. [🗂️ テストリソース](#テストリソース)
16. [🚀 テストの実施方法](#テストの実施方法)
17. [📚 参考資料](#参考資料)

---

## 🎯 目的・ポリシー
### テストを書く目的
- **デグレードの検出**
機能追加やリファクタリングの際、既存の動作が損なわれていないかを自動で検証する。
- **仕様の明文化**
テストコードを「そのクラスがどう動くべきか」を定義する生きたドキュメントとして機能させる。
- **設計の改善**
テストの書きにくさから依存関係の密結合を検知し、設計上の問題を早期に解消する。

### ポリシー
- **自動実行の徹底**
テストはすべて自動実行可能とする。手動操作を介在させてはならない。
- **独立性の確保**
各テストは完全に独立させる。他のテストの実行順序や結果に依存してはならない。
- **再現性の担保**
実行条件が同じであれば常に同一の結果を出す。ランダム値、現在時刻、外部サービスへの依存を排除する。
- **テスト容易性の優先**
テストしやすい設計を最優先する。検証のためにアクセス修飾子を緩和する妥協は認めるが、不要な複雑さをプロダクションコードに持ち込んではならない。
- **原因特定プロセスの簡略化**
テスト失敗時の原因特定を容易にする。原則として「1テスト1アサーション」とし、複数の検証を行う場合は詳細なメッセージを付与する。
- **実行速度の維持**
CIでの実行速度を重視する。数秒以上を要するテストは `[Explicit]` 属性を付与し、通常の実行サイクルから除外する。

## 📖 概要

Unityのテストフレームワークは **NUnit** ベースで、Unity Test Framework パッケージ (`com.unity.test-framework`) が提供します。

テストは **EditMode** と **PlayMode** の2種類があります。

| 種類 | 実行環境 | 用途 |
|------|---------|------|
| EditMode | エディタ（非再生） | ロジック単体テスト、エディタ拡張のテスト |
| PlayMode | 再生モード or スタンドアロンビルド | MonoBehaviourのライフサイクル、Scene、Coroutineを含むテスト |

---

## 📦 必要パッケージ

### テスト関連（必須）

`Packages/manifest.json` の `dependencies` に以下を追加してください。

| パッケージ | 取得元 | 用途 |
|-----------|--------|------|
| `com.unity.test-framework` | Unity公式 | UnityテストフレームワークのコアAPI |
| `net.tnrd.nsubstitute` | OpenUPM | モック・スタブ生成ライブラリ（NSubstitute） |
| `com.nowsprinting.test-helper` | OpenUPM | `[CreateScene]`、`[LoadScene]` などの補助アトリビュート |

NSubstituteとtest-helperはOpenUPMのスコープ登録が必要です。

```json:Packages/manifest.json
"scopedRegistries": [
  {
    "name": "package.openupm.com",
    "url": "https://package.openupm.com",
    "scopes": [
      "com.nowsprinting",
      "net.tnrd.nsubstitute"
    ]
  }
]
```

### InputSystem のテストAPIを使う場合

`manifest.json` の `testables` にも追加してください。

```json:Packages/manifest.json
"testables": [
  "com.unity.inputsystem"
]
```

---

## 🔧 アセンブリ定義（.asmdef）

### メインスクリプトのアセンブリ化

テストアセンブリがメインスクリプトを参照するには、メインスクリプト側にも `.asmdef` が必要です。`autoReferenced: true` にしておくことで、テスト側から名前指定で参照できます。

```
Assets/Scripts/{プロジェクト名}/
└── {プロジェクト名}.asmdef   ← これがないとテストから参照できない
```

```json
{
    "name": "{プロジェクト名}",
    "rootNamespace": "{プロジェクト名}",
    "autoReferenced": true
}
```

エディタ専用スクリプト（`Assets/Scripts/.../Editor/`）は別途 `Editor.asmdef` を作り、`includePlatforms: ["Editor"]` を指定してください。

#### ⚠️ アセンブリ化による注意点

`.asmdef` を配置するとその配下のスクリプトは **明示的なアセンブリ** に属します。これにより以下の点に注意が必要です。

**Unity暗黙アセンブリとの分離**

`.asmdef` を置く前は、プロジェクト内の全スクリプトが Unity の暗黙的なアセンブリ（`Assembly-CSharp` など）に属していました。`.asmdef` を置いた後は、**そのフォルダ配下のスクリプトは明示的アセンブリに移動し、暗黙アセンブリのスクリプトからは参照できなくなります**（逆方向は可能）。

具体的には以下のような問題が起きる場合があります。

- `.asmdef` を置いたフォルダのスクリプトが、まだ `.asmdef` を持たない別フォルダのスクリプトに依存している場合、コンパイルエラーになります。
- `Assembly-CSharp` に属するスクリプトは `references` の指定なしに明示的アセンブリを参照できないため、段階的に移行する場合は依存関係の順序に注意してください。

**`internal` アクセスの制限**

明示的アセンブリに移動したクラスの `internal` メンバーは、同一アセンブリ内からしかアクセスできなくなります。テストから `internal` にアクセスしたい場合は `AssemblyInfo.cs` で `InternalsVisibleTo` を設定してください。

```csharp:Assets/Scripts/{プロジェクト名}/AssemblyInfo.cs
using System.Runtime.CompilerServices;
[assembly: InternalsVisibleTo("{プロジェクト名}.Editor.Tests")]
[assembly: InternalsVisibleTo("{プロジェクト名}.Runtime.Tests")]
```

**EditorスクリプトとRuntime依存の分離**

エディタ専用クラスはランタイムアセンブリから参照できないため、エディタコードとランタイムコードを明確に分ける必要があります。これは設計上望ましい分離でもあります。

### EditMode テスト用：`Editor.Tests.asmdef`

```json
{
    "name": "{プロジェクト名}.Editor.Tests",
    "references": [
        "UnityEngine.TestRunner",
        "UnityEditor.TestRunner",
        "UniTask",
        "{プロジェクト名}",
        "{プロジェクト名}.Editor",
        "TNRD.NSubstitute",
        "TestHelper",
        "VContainer"
    ],
    "includePlatforms": ["Editor"],
    "overrideReferences": true,
    "precompiledReferences": ["nunit.framework.dll"],
    "autoReferenced": false,
    "defineConstraints": ["UNITY_INCLUDE_TESTS"]
}
```

### PlayMode テスト用：`Runtime.Tests.asmdef`

```json
{
    "name": "{プロジェクト名}.Runtime.Tests",
    "references": [
        "UnityEngine.TestRunner",
        "UnityEditor.TestRunner",
        "UniTask",
        "{プロジェクト名}",
        "TNRD.NSubstitute",
        "VContainer"
    ],
    "includePlatforms": [],
    "excludePlatforms": ["LinuxStandalone64"],
    "overrideReferences": true,
    "precompiledReferences": ["nunit.framework.dll"],
    "autoReferenced": false,
    "defineConstraints": ["UNITY_INCLUDE_TESTS"]
}
```

**ポイント：**
- `autoReferenced: false` — テスト用アセンブリは自動参照しません。
- `defineConstraints: ["UNITY_INCLUDE_TESTS"]` — テストビルド時のみコンパイルされます。
- EditMode は `includePlatforms: ["Editor"]` を指定します。
- PlayMode は `includePlatforms` を空にします（全プラットフォーム対象）。
- 使用するパッケージに応じて `references` を追加してください（`MasterMemory`, `Unity.InputSystem` など）。

### `csc.rsp`

コンパイラオプションを指定するファイルです。各テストフォルダ直下に配置してください。

NSubstitute を使うと `CS8600`（null 許容参照型の警告）などが大量に出る場合があるため、テストアセンブリでは以下のように警告を抑制します。

```text:csc.rsp
-nullable:disable
```

特定の警告IDだけ抑制する場合。

```text:csc.rsp
-nowarn:CS8600,CS8602,CS8603
```

---

## 📁 ファイル配置

```
Assets/
├── Scripts/
│   └── {プロジェクト名}/
│       ├── {プロジェクト名}.asmdef   ← メインスクリプトのアセンブリ定義
│       ├── AssemblyInfo.cs           ← InternalsVisibleTo の設定（必要な場合）
│       ├── Editor/
│       │   └── Editor.asmdef         ← エディタ専用スクリプトのアセンブリ定義
│       └── ...
└── Tests/
    └── {プロジェクト名}/
        ├── Editor/                          ← EditMode テスト
        │   ├── Editor.Tests.asmdef
        │   ├── csc.rsp
        │   ├── Examples/                    ← サンプルテスト（参考用）
        │   ├── Character/                   ← テスト対象ドメインごとにフォルダを切る
        │   ├── Database/
        │   └── ...
        ├── Runtime/                         ← PlayMode テスト
        │   ├── Runtime.Tests.asmdef
        │   ├── csc.rsp
        │   ├── Examples/                    ← サンプルテスト（参考用）
        │   ├── Character/
        │   ├── Stage/
        │   └── ...
        └── TestResources/                   ← テスト用アセット（Scene等）
            └── Scenes/
                └── ExampleScene.unity
```

**ルール：**
- `Assets/Tests/{プロジェクト名}/Editor/` に EditMode テストを置いてください。
- `Assets/Tests/{プロジェクト名}/Runtime/` に PlayMode テストを置いてください。
- テスト対象のドメイン（機能）ごとにサブフォルダを切ってください。
- テスト用アセットは `TestResources/` に置いてください。

---

## 🔀 テストの種類と使い分け

| アトリビュート | 種別 | 説明 |
|--------------|------|------|
| `[Test]` | EditMode / PlayMode | 通常の同期テスト |
| `[UnityTest]` | EditMode / PlayMode | `IEnumerator` を返すコルーチンテスト。`yield return null` で1フレーム待機できます |
| `async Task` / `async UniTask` | EditMode | `await` を使った非同期テスト |

---

## 🏗️ 基本構造・ライフサイクル

```csharp
using NUnit.Framework;
using UnityEngine.TestTools;
using System.Collections;

namespace {プロジェクト名}.Tests.Editor.SomeFeature
{
    public class SomeFeatureTest
    {
        [OneTimeSetUp]
        public void OneTimeSetUp()
        {
            // クラス内の最初のテスト実行前に1回だけ呼ばれる
        }

        [SetUp]
        public void SetUp()
        {
            // 各テストの実行前に呼ばれる
        }

        [UnitySetUp]
        public IEnumerator UnitySetUp()
        {
            // 各テストの実行前に呼ばれる（コルーチン版）
            yield return null;
        }

        [Test]
        public void テストメソッド名_状況_期待する結果()
        {
            // Arrange（準備）
            // Act（実行）
            // Assert（検証）
            Assert.That(actual, Is.EqualTo(expected));
        }

        [TearDown]
        public void TearDown()
        {
            // 各テストの実行後に呼ばれる
        }

        [UnityTearDown]
        public IEnumerator UnityTearDown()
        {
            // 各テストの実行後に呼ばれる（コルーチン版）
            yield return null;
        }

        [OneTimeTearDown]
        public void OneTimeTearDown()
        {
            // クラス内の最後のテスト実行後に1回だけ呼ばれる
        }
    }
}
```

**ライフサイクル実行順：**
`OneTimeSetUp` → 各テスト毎に（`SetUp` → `UnitySetUp` → テスト本体 → `UnityTearDown` → `TearDown`） → `OneTimeTearDown`

**命名規則：**
- ファイル名：`{テスト対象クラス名}Test.cs`
- テストメソッド名：日本語可。`{メソッド名}_{状況}_{期待する結果}` の形式が望ましいです。
- namespace：`{プロジェクト名}.Tests.Editor.<ドメイン>` または `{プロジェクト名}.Tests.Runtime.<ドメイン>`

---

## ✅ アサーション

NUnit の `Assert.That(actual, constraint)` 形式を使います。

```csharp
// 等値
Assert.That(actual, Is.EqualTo(expected));
Assert.That(actual, Is.Not.EqualTo(unexpected));

// 近似値（浮動小数点）
Assert.That(actual, Is.EqualTo(expected).Within(0.001));
Assert.That(actual, Is.EqualTo(expected).Within(1).Percent);
FloatEqualityComparer comparer = new(0.1f);
Assert.That(actual, Is.EqualTo(expected).Using(comparer));

// bool
Assert.That(condition, Is.True);
Assert.That(condition, Is.False);

// null
Assert.That(obj, Is.Null);
Assert.That(obj, Is.Not.Null);

// 型
Assert.That(obj, Is.InstanceOf<SomeClass>());

// 大小
Assert.That(value, Is.GreaterThan(min));
Assert.That(value, Is.LessThan(max));
Assert.That(value, Is.InRange(min, max));

// コレクション（順序一致）
Assert.That(actual, Is.EqualTo(new[] { 1, 2, 3 }));

// コレクション（順不同）
Assert.That(actual, Is.EquivalentTo(new[] { 3, 1, 2 }));

// 例外
Assert.Throws<SomeException>(() => sut.Method());

// GCアロケーションなし
Assert.That(() => sut.Method(), Is.Not.AllocatingGCMemory());

// ログアサーション
LogAssert.Expect(LogType.Error, "expected error message");
Debug.LogError("expected error message");
LogAssert.NoUnexpectedReceived();

// メッセージ付きアサーション（失敗箇所の特定が楽になる）
Assert.That(actual, Is.EqualTo(expected), "失敗時のメッセージ");
```

### ログ関連アトリビュート

```csharp
// 予期しないログ出力をテスト失敗として扱う
[Test, TestMustExpectAllLogs]
public void ログが出ないことを保証するテスト() { ... }

// すべてのログを無視する（テスト内でも設定可）
LogAssert.ignoreFailingMessages = true;
```

---

## 🔢 パラメータ化テスト

```csharp
// ケース数が少ない場合
[TestCase(10, 20, 30)]
[TestCase(100, -50, 50)]
public void TestCaseの例(int a, int b, int expected)
{
    Assert.That(a + b, Is.EqualTo(expected));
}

// ケース数が多い場合
private static object[] _testCases =
{
    new object[] { 10, 20, 30 },
    new object[] { 100, -50, 50 },
};
[TestCaseSource(nameof(_testCases))]
public void TestCaseSourceの例(int a, int b, int expected)
{
    Assert.That(a + b, Is.EqualTo(expected));
}

// 動的生成
private static IEnumerable<object[]> DynamicTestCases()
{
    yield return new object[] { 10, 20, 30 };
}
[TestCaseSource(nameof(DynamicTestCases))]
public void 動的TestCaseSourceの例(int a, int b, int expected) { ... }

// 総当たり（引数の組み合わせ全てを実行）
[Test]
public void Valuesの例([Values(1, 2, 3)] int a, [Values("A", "B")] string b) { ... }

// 範囲指定
[Test]
public void Rangeの例([Range(1, 5)] int a, [Range(10, 50, 10)] int b) { ... }
```

> ランダム値テスト（`[Random]`）は再現性がないため、テストダブルで入力を固定する方法を優先してください。

---

## 🚫 テストの除外（Explicit / Ignore）

### Explicit

通常の「全テスト実行」には含まれませんが、Test Runnerから個別指定するか、カテゴリフィルタで指定した場合には実行されます。一時的に通常実行から外したいが、必要なときは動かしたいケースに使います。

```csharp
// メソッド単位
[Test]
[Explicit("依存ライブラリのバグ修正が終わるまで実行対象から外す")]
public void 重いテスト() { }

// クラス単位
[Explicit("実行に数時間かかる統合テストなので実行対象から外す")]
public class HeavyIntegrationTest
{
    [Test]
    public void すごく重いテスト() { }
}

// アセンブリ単位（AssemblyInfo.cs に記述）
[assembly: Explicit("仕様を再検討するので一時的にアセンブリごと除外する")]
```

### Ignore

常に除外されます。`Explicit` と異なり、カテゴリ指定や個別指定でも実行されません。形だけ残したいコードに使います。

```csharp
// メソッド単位
[Test]
[Ignore("現在は使用されていない機能なので除外")]
public void 廃止予定のテスト() { }

// クラス単位
[Ignore("まだ実装が不完全なので除外")]
public class IncompleteTest
{
    [Test]
    public void なんかしらのテスト() { }
}
```

| | Explicit | Ignore |
|---|---|---|
| 通常の全テスト実行 | 除外 | 除外 |
| カテゴリ・個別指定での実行 | 実行される | 除外 |

---

## 🎭 テストダブル（NSubstitute）

インターフェースや抽象クラスに依存するクラスをテストする際に使用します。

```csharp
using NSubstitute;

// スタブ（間接入力の固定）
var stub = Substitute.For<IFoo>();
stub.Method(arg).Returns(value);
stub.Method(arg).Returns(val1, val2, val3); // 順番に返す

// スパイ（間接出力の検証）
var spy = Substitute.For<IFoo>();
sut.DoSomething(spy);
spy.Received().Method(expectedArg);               // 呼ばれたことを検証
spy.DidNotReceive().Method(unexpectedArg);        // 呼ばれていないことを検証
spy.Received(2).Method(Arg.Any<int>());           // 2回呼ばれたことを検証

// 引数マッチャー
Arg.Any<int>()                   // 任意の値
Arg.Is<int>(x => x > 0)         // 条件一致

// イベント
mock.SomeEvent += Raise.Event<EventHandler>(EventArgs.Empty);

// 具象クラス・抽象クラスの部分モック
var partial = Substitute.ForPartsOf<AbstractClass>(ctorArg);
```

---

## ⏳ 非同期テスト（UniTask）

```csharp
using System.Threading.Tasks;
using Cysharp.Threading.Tasks;

// UniTask を await できる
[Test]
public async Task UniTaskを使った非同期テスト()
{
    var result = await sut.AsyncMethod();
    Assert.That(result, Is.EqualTo(expected));
}

// 非同期の例外検証はTryCatchで行う
[Test]
public async Task 非同期例外の検証()
{
    try
    {
        await sut.AsyncMethodThatThrows();
        Assert.Fail("例外が発生することを期待している");
    }
    catch (SomeException ex)
    {
        Assert.That(ex.Message, Is.EqualTo("expected message"));
    }
}

// UnityTestでUniTaskを使う場合
[UnityTest]
public IEnumerator UnityTestでUniTaskを使う() => UniTask.ToCoroutine(async () =>
{
    await sut.AsyncMethod();
    Assert.That(condition, Is.True);
});
```

> `Assert.ThrowsAsync` は `async` メソッドでは無限待機になるため使用しないでください。

---

## ▶️ PlayModeテスト固有のトピック

### MonoBehaviourのテスト

```csharp
using UnityEngine.TestTools;

public class SutMonoBehavior : MonoBehaviour, IMonoBehaviourTest
{
    public bool IsTestFinished
    {
        get
        {
            // trueを返すとテスト終了
            Assert.That(someCondition, Is.True);
            return true;
        }
    }
}
```

`IsTestFinished` が毎フレーム評価されるので、フレーム依存のライフサイクルテストに使用します。

### Sceneを使うテスト

```csharp
using TestHelper.Attributes;

// クリーンなSceneを生成して使う
[Test]
[CreateScene(camera: true, light: true)]
public void CreateSceneの例() { ... }

// ScenesInBuildに含まれているSceneを使う（PlayMode専用）
[UnityTest]
public IEnumerator ScenesInBuildのSceneを使う()
{
    yield return SceneManager.LoadSceneAsync("SceneName");
    // ...
}

// ScenesInBuildに含まれていないSceneを使う
[Test]
[LoadScene("Assets/Tests/{プロジェクト名}/TestResources/Scenes/ExampleScene.unity")]
public void LoadSceneの例() { ... }
```

### ビルド前後の処理（スタンドアロンビルドテスト）

スタンドアロンビルドでは `AssetDatabase` が使用不可のため、`Resources` を使う方法があります。

```csharp
public class BuildSetup : IPrebuildSetup, IPostBuildCleanup
{
    public void Setup()   // ビルド前に実行
    {
#if UNITY_EDITOR
        UnityEditor.AssetDatabase.CreateFolder("Assets/Tests", "Resources");
        UnityEditor.FileUtil.CopyFileOrDirectory("Assets/Prefabs", "Assets/Tests/Resources/Prefabs");
        UnityEditor.AssetDatabase.Refresh();
#endif
    }

    public void Cleanup() // ビルド後に実行
    {
#if UNITY_EDITOR
        UnityEditor.AssetDatabase.DeleteAsset("Assets/Tests/Resources");
#endif
    }
}

[PrebuildSetup(typeof(BuildSetup))]
[PostBuildCleanup(typeof(BuildSetup))]
public class SomeTest { ... }
```

---

## 💉 VContainerとの組み合わせ

VContainerのDIを使うクラスをテストする場合、テスト専用の `LifetimeScope` をセットアップで構築し、テスト終了時に破棄します。

### 基本パターン

```csharp
using VContainer;
using VContainer.Unity;
using NSubstitute;

public class SomeServiceTest
{
    private LifetimeScope _scope;

    // [Inject] を付けると _scope.Container.Inject(this) でフィールドに注入される
    [Inject] private ISomeService _someService;

    [UnitySetUp]
    public IEnumerator UnitySetUp() => UniTask.ToCoroutine(async () =>
    {
        // スタブの準備
        var stubDependency = Substitute.For<IDependency>();
        stubDependency.SomeMethod().Returns(42);

        // テスト用コンテナの構築
        _scope = LifetimeScope.Create(builder =>
        {
            builder.RegisterComponent(stubDependency);  // スタブを登録
            builder.Register<SomeService>(Lifetime.Singleton).As<ISomeService>();
        }, GetType().Name);

        // このテストクラス自身に注入
        _scope.Container.Inject(this);
    });

    [TearDown]
    public void TearDown()
    {
        _scope.Dispose(); // 必ず破棄する
    }

    [Test]
    public void SomeServiceの動作確認()
    {
        var result = _someService.Execute();
        Assert.That(result, Is.EqualTo(expected));
    }
}
```

### 既存のInstallerを再利用するパターン

プロダクションコードのInstallerをそのまま利用しつつ、特定の依存だけスタブに差し替えます。

```csharp
[UnitySetUp]
public IEnumerator UnitySetUp() => UniTask.ToCoroutine(async () =>
{
    var stubFoo = Substitute.For<IFoo>();
    stubFoo.Bar().Returns(UniTask.CompletedTask);

    _scope = LifetimeScope.Create(builder =>
    {
        // スタブを先に登録（後から登録したものが優先される）
        builder.RegisterComponent(stubFoo);

        // 既存のInstallerをそのまま使う
        new SomeFeatureInstaller().Install(builder);
        new AnotherInstaller().Install(builder);
    }, GetType().Name);

    _scope.Container.Inject(this);
});
```

**注意事項：**
- `_scope.Dispose()` を `TearDown` で必ず呼んでください（呼ばないと次のテストに影響します）。
- スタブを登録する際、Installerとの登録順序に注意してください（後勝ち）。
- `MonoBehaviour` に紐づく依存は `RegisterComponent` で登録してください。

---

## 🗂️ テストリソース

テストで使用するSceneやPrefabなどのアセットは `Assets/Tests/{プロジェクト名}/TestResources/` 以下に置いてください。

```
Assets/Tests/{プロジェクト名}/TestResources/
└── Scenes/
    └── ExampleScene.unity   ← [LoadScene] で参照する
```

`[LoadScene]` アトリビュートではリポジトリルートからのフルパスで指定します。

---

## 🚀 テストの実施方法

### エディタ上での実行

Unity Editor のメニュー `Window > General > Test Runner` を開いてください。

EditMode / PlayMode タブを切り替えて「Run All」ボタンで全テストを実行できます。個別のテストやクラスは右クリックメニューから実行できます。

カテゴリフィルタで絞り込む場合は Test Runner ウィンドウ右上のフィルタアイコンから設定してください。

### コマンドラインでの実行（ローカル）

```bash
# EditMode テストの実行
unity-editor -nographics -runTests \
  -testPlatform EditMode \
  -testFilter "{プロジェクト名}.Tests.*" \
  -testResults ./reports/editor-test-result.xml

# PlayMode テストの実行
unity-editor -nographics -runTests \
  -testPlatform PlayMode \
  -testFilter "{プロジェクト名}.Tests.*" \
  -testResults ./reports/playmode-test-result.xml
```

### CI での実行

社内CI共通基盤の **ss-fleet-ci** を利用すると、Unity テストのCIセットアップを簡単に導入できます。

#{4096181}

---

## 📚 参考資料

### 書籍

Unity Test Framework の体系的な解説として、以下の電子書籍を参照することを推奨します。いずれもファイルサーバーに保存されています。

- **[Unity Test Framework完全攻略ガイド 第2版](https://www.nowsprinting.com/entry/2022/08/10/080000)**
  EditMode・PlayModeテストの基本から応用までをカバーした主要リファレンスです。

- **[Unity Test Framework完全攻略ガイド 統合テスト編](https://www.nowsprinting.com/entry/2023/05/21/043237)**
  シーンを使った統合テストやビルドテストの手法を解説しています。上記第2版の続編にあたります。

### MCPによる自動プレイ・エージングテスト

エージングテストなど、長時間にわたるゲームの自動プレイが必要なテストシナリオでは、AIエージェントにゲームをプレイさせる方法が有効です。Unity製ゲームのランタイムにMCPサーバを組み込み、ClaudeなどのAIエージェントから操作させることができます。

- **[Gameplay MCP Server for Unity を公開しました](https://www.nowsprinting.com/entry/2026/03/08/125656)**

### 公式ドキュメント

- [Unity Test Framework マニュアル](https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/index.html)
- [NSubstitute ドキュメント](https://nsubstitute.github.io/)
- [test-helper パッケージ](https://github.com/nowsprinting/test-helper)
