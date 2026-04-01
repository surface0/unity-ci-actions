#!/usr/bin/env python3
"""
unity_utils.py

Unityのコマンドライン実行に関連する共通処理をまとめたユーティリティモジュールです。
- プロジェクトからのUnityバージョンの取得
- Unity HubからのUnity実行ファイルの検索
- Unityプロセスの実行とログ監視
"""

import os
import re
import subprocess
import sys
from pathlib import Path

def get_unity_version(project_path: Path) -> str:
    """
    指定されたUnityプロジェクトのProjectVersion.txtから
    使用されているUnityのバージョン文字列を抽出します。
    """
    version_file = project_path / "ProjectSettings" / "ProjectVersion.txt"
    if not version_file.exists():
        raise RuntimeError("ProjectVersion.txt not found")
    
    text = version_file.read_text(encoding="utf-8")
    
    # 正規表現で "m_EditorVersion: 2022.3.x..." の形式からバージョン部分を抽出
    m = re.search(r"m_EditorVersion:\s*(.+)", text)
    if not m:
        raise RuntimeError("Unity version not found")
        
    return m.group(1).strip()

def find_unity_exe(version: str | None) -> tuple[Path, str]:
    """
    指定されたバージョンに合致するUnity実行ファイルのパスを検索します。
    環境変数 UNITY_HUB_EDITOR_PATH があればそこから探し、なければ適切なコマンド名を返します。
    OSによって実行ファイル名が異なります (Win: "Unity.exe", Linux: "unity-editor")。
    """
    # OSに応じて実行ファイル名を決定
    if sys.platform.startswith("linux"):
        unity_exe_name = "unity-editor"
    else:  # Windows
        unity_exe_name = "Unity.exe"

    hub_editor_path = os.environ.get("UNITY_HUB_EDITOR_PATH")

    if hub_editor_path:
        hub_editor_dir = Path(hub_editor_path)
        if not hub_editor_dir.exists():
            raise RuntimeError(f"UNITY_HUB_EDITOR_PATH is set, but directory not found: {hub_editor_dir}")

        if version:
            # 完全一致で検索
            unity_path = hub_editor_dir / version / "Editor" / unity_exe_name
            if unity_path.exists():
                return unity_path, version

            # 前方一致で検索
            for d in hub_editor_dir.iterdir():
                if d.is_dir() and d.name.startswith(version):
                    unity_path = d / "Editor" / unity_exe_name
                    if unity_path.exists():
                        print(f"Found matching Unity version: {d.name}")
                        return unity_path, d.name
            
            raise RuntimeError(f"Unity version '{version}' not found in '{hub_editor_dir}'")
        else:
            # バージョン未指定時は、最新のものを取得
            editors = sorted(
                [d for d in hub_editor_dir.iterdir() if d.is_dir()],
                key=lambda d: d.name,
                reverse=True,
            )
            for editor_dir in editors:
                unity_path = editor_dir / "Editor" / unity_exe_name
                if unity_path.exists():
                    print(f"Unity version not specified, using latest from Hub: {editor_dir.name}")
                    return unity_path, editor_dir.name
            
            raise RuntimeError(f"No Unity installation found in {hub_editor_dir}")

    # UNITY_HUB_EDITOR_PATH がない場合、適切なコマンド名を返す
    print(f"UNITY_HUB_EDITOR_PATH not set. Using '{unity_exe_name}' command from PATH.")
    
    return Path(unity_exe_name), "unknown"

def run_unity(unity: Path, project: Path | None, unity_args: list[str], dry_run: bool = False):
    """
    指定された引数でUnityをバッチモードで実行し、標準出力を監視して
    エラーが発生していないかチェックします。
    """
    # エラーとみなすログのキーワード定義
    FAIL_PATTERNS = [
        "Build Failed",
        "Compilation failed",
        "Scripts have compiler errors",
        "Aborting batchmode due to failure",
        "LICENSE SYSTEM IS NOT INITIALIZED",
    ]

    # 基本コマンドの組み立て（バッチモード、グラフィックなし）
    cmd = [str(unity), "-batchmode", "-nographics"]
    
    if project:
        cmd.extend(["-projectPath", str(project)])
        
    cmd.extend(unity_args)
    
    if "-quit" not in unity_args:
        cmd.append("-quit")
        
    # ログを標準出力に流す
    cmd.extend(["-logFile", "-"])

    print(f"Executing Unity command: {' '.join(cmd)}")

    # dry-runの場合はコマンドを表示するだけで終了
    if dry_run:
        print("Dry-run mode: command not executed.")
        return 0

    # サブプロセスとしてUnityを実行
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    has_failed = False
    
    # ログを逐次読み込みながらエラーパターンを検知
    for line_bytes in process.stdout:
        # 生のバイト列をそのまま標準出力に流すことで、エンコーディングエラーを回避
        sys.stdout.buffer.write(line_bytes)
        sys.stdout.buffer.flush()

        # エラー検知用に文字列化（不正なバイトは置換）
        line_str = line_bytes.decode("utf-8", errors="replace")
        if not has_failed:
            for pattern in FAIL_PATTERNS:
                if pattern in line_str:
                    has_failed = True
                    print(f"\nDetected failure pattern: {pattern}")
                    break

    process.wait()

    if has_failed:
        print("Unity command failed.")
        return 1

    return process.returncode
