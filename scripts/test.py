#!/usr/bin/env python3
"""
test.py

UnityプロジェクトのEditMode/PlayModeテストをバッチモードで実行するスクリプトです。
テスト結果は com.nowsprinting.test-helper の JUnit XML 形式で出力されます。
"""

import argparse
import sys
from pathlib import Path
from unity_utils import get_unity_version, find_unity_exe, run_unity


def main():
    # 引数の解析
    parser = argparse.ArgumentParser(description="Run Unity tests")
    parser.add_argument("--project", default=".", help="Unity project path")
    parser.add_argument(
        "--platform",
        default="EditMode",
        choices=["EditMode", "PlayMode"],
        help="Test platform (EditMode or PlayMode)",
    )
    parser.add_argument(
        "--results",
        default="test-results.xml",
        help="Test results output path (JUnit XML format)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not execute the test command")
    args = parser.parse_args()

    try:
        # プロジェクトパスの解決とバージョンの取得
        project_path = Path(args.project).resolve()
        initial_unity_version = get_unity_version(project_path)
        print(f"Project requires Unity version: {initial_unity_version}")

        # 使用するUnity実行ファイルの特定
        unity_exe, found_unity_version = find_unity_exe(initial_unity_version)
        print(f"Found Unity executable: {unity_exe} (Version: {found_unity_version})")

        # テスト実行用コマンド引数の構築
        # -testHelperJUnitResults: com.nowsprinting.test-helper による JUnit XML 形式の出力
        results_path = Path(args.results).resolve()
        unity_args = [
            "-runTests",
            "-testPlatform", args.platform,
            "-testHelperJUnitResults", str(results_path),
        ]

        # Unityの実行
        exit_code = run_unity(unity_exe, project_path, unity_args, dry_run=args.dry_run)
        sys.exit(exit_code)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
