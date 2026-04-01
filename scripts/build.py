#!/usr/bin/env python3
"""
build.py

Unityプロジェクトのビルドを実行するスクリプトです。
指定された静的メソッド（例: BuildScript.Build）をバッチモードで呼び出してビルドを行います。
"""

import argparse
import os
import sys
from pathlib import Path
from unity_utils import get_unity_version, find_unity_exe, run_unity

def main():
    # 引数の解析
    parser = argparse.ArgumentParser(description="Build the Unity project")
    parser.add_argument("--project", default=".", help="Unity project path")
    parser.add_argument("--method", required=True, help="Method to execute (e.g., BuildScript.Build)")
    parser.add_argument("--target", default="Switch", help="Build target (e.g., Switch, StandaloneWindows64)")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute the build command")
    args = parser.parse_args()

    try:
        # プロジェクトパスの解決とバージョンの取得
        project_path = Path(args.project).resolve()
        initial_unity_version = get_unity_version(project_path)
        print(f"Project requires Unity version: {initial_unity_version}")

        # 使用するUnity実行ファイルの特定
        unity_exe, found_unity_version = find_unity_exe(initial_unity_version)
        print(f"Found Unity executable: {unity_exe} (Version: {found_unity_version})")

        # ビルド用コマンド引数の構築
        # -buildTarget で対象プラットフォームを指定
        # -executeMethod でビルド処理を行うC#のメソッドを指定
        unity_args = ["-buildTarget", args.target, "-executeMethod", args.method]
        
        # Unityの実行
        exit_code = run_unity(unity_exe, project_path, unity_args, dry_run=args.dry_run)
        sys.exit(exit_code)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
