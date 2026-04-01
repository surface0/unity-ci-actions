#!/usr/bin/env python3
"""
test.py

Unityのテスト（PlayMode/EditMode）を実行するスクリプトです。
指定されたプラットフォームでテストを実行し、XML形式で結果を出力します。
"""

import argparse
import sys
from pathlib import Path
from unity_utils import get_unity_version, find_unity_exe, run_unity

def main():
    # 引数の解析
    parser = argparse.ArgumentParser(description="Run Unity tests")
    parser.add_argument("--project", default=".", help="Unity project path")
    parser.add_argument("--test-platform", default="PlayMode", help="Test platform to run (PlayMode/EditMode)")
    parser.add_argument("--test-results", default="test-results.xml", help="Path for output test results XML")
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
        unity_args = [
            "-runTests",
            "-testPlatform", args.test_platform,
            "-testResults", args.test_results,
        ]
        
        # Unityの実行
        exit_code = run_unity(unity_exe, project_path, unity_args)
        sys.exit(exit_code)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
