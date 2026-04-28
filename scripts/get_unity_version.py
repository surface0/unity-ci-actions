#!/usr/bin/env python3
"""
get_unity_version.py

Unityプロジェクトのバージョンを取得するだけのシンプルなスクリプトです。
CIのワークフローなどで、環境変数にバージョンを設定する際などに利用されます。
"""

import argparse
from pathlib import Path
import sys
from unity_utils import get_unity_version

def main():
    # 引数の解析
    parser = argparse.ArgumentParser(description="Get Unity project version")
    parser.add_argument(
        "--project", default=".", help="Unity project path (default: current directory)"
    )
    args = parser.parse_args()

    try:
        # プロジェクトパスの解決
        project_path = Path(args.project).resolve()
        
        # ユーティリティ関数を使ってProjectVersion.txtからバージョンを取得
        unity_version = get_unity_version(project_path)
        
        # 取得したバージョンを標準出力に出力（CIなどで変数にキャプチャするため）
        print(unity_version)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
