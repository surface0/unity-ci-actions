#!/usr/bin/env python3
"""
activate.py

Unityのライセンス認証（アクティベーション）を行うスクリプトです。

サブコマンド:
  generate-alf              ALFファイルを生成します（ULF取得のための事前手順）
  activate --license-file   ULFファイルを指定してライセンスを認証します
"""

import argparse
import sys
from pathlib import Path
from unity_utils import get_unity_version, find_unity_exe, run_unity


def resolve_unity(project_arg: str):
    project_path = Path(project_arg).resolve()
    version = get_unity_version(project_path)
    print(f"Project requires Unity version: {version}")
    unity_exe, found_version = find_unity_exe(version)
    print(f"Found Unity executable: {unity_exe} (Version: {found_version})")
    return unity_exe


def cmd_generate_alf(args):
    unity_exe = resolve_unity(args.project)
    exit_code = run_unity(unity_exe, None, ["-createManualActivationFile"])
    sys.exit(exit_code)


def cmd_activate(args):
    unity_exe = resolve_unity(args.project)
    exit_code = run_unity(unity_exe, None, ["-manualLicenseFile", args.license_file])
    sys.exit(exit_code)


def main():
    parser = argparse.ArgumentParser(description="Unity license management")
    parser.add_argument("--project", default=".", help="Unity project path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate-alf", help="Generate ALF file for manual activation")

    activate_parser = subparsers.add_parser("activate", help="Activate Unity with a ULF file")
    activate_parser.add_argument("--license-file", required=True, help="Path to the Unity license file (.ulf)")

    args = parser.parse_args()

    try:
        if args.command == "generate-alf":
            cmd_generate_alf(args)
        elif args.command == "activate":
            cmd_activate(args)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
