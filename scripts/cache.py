#!/usr/bin/env python3
"""
cache.py

指定されたディレクトリをtarとzstdを用いて圧縮・解凍し、
キャッシュとして保存・復元するスクリプトです。
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
import argparse
import stat
import tarfile
from concurrent.futures import ThreadPoolExecutor


def remove_readonly(func, path, excinfo):
    """
    shutil.rmtreeでアクセス拒否エラーが出た場合に、
    読み取り専用属性を解除して再試行するためのエラーハンドラ。
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def sanitize_filename(name: str) -> str:
    """
    ファイル名として使用できない無効な文字をアンダースコアに置換します。
    Windows, Linux, macOS の一般的な禁則文字に対応しています。
    """
    # A basic set of invalid characters for Windows/Linux/macOS
    invalid_chars = r'<>:"/\|?*'
    sanitized_name = name
    for char in invalid_chars:
        sanitized_name = sanitized_name.replace(char, '_')
    return sanitized_name


def write_file_concurrent(member_data: bytes, dest_path: str):
    """
    別スレッドでファイルへの書き込みを行うヘルパー関数。
    """
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'wb') as f:
        f.write(member_data)


def save_cache(project_path: Path, cache_dir: str, target_dir: str, cache_key: str):
    """
    指定された対象ディレクトリをtar形式でアーカイブし、zstdで圧縮してキャッシュディレクトリに保存します。
    """
    sanitized_key = sanitize_filename(cache_key)
    cache_root_dir = Path(cache_dir).resolve()
    # ディレクトリが存在しない場合は作成
    cache_root_dir.mkdir(parents=True, exist_ok=True)

    cache_file = cache_root_dir / f"{sanitized_key}.tar.zst"
    target_dir_path = project_path / target_dir

    print(f"Saving cache for key: {cache_key} (sanitized to: {sanitized_key}) to {cache_file}")
    if not target_dir_path.exists():
        print(f"Target directory {target_dir_path} does not exist. Skipping cache save.", file=sys.stderr)
        return 0

    tmp_path = None
    try:
        # 一時ファイルに書き込んでからアトミックにリネームする（同時アクセス対策）
        with tempfile.NamedTemporaryFile(
            dir=cache_root_dir, suffix='.tar.zst.tmp', delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)

        print(f"Creating and compressing tar archive to {cache_file} using Python tarfile's native zstd support...")
        with tarfile.open(name=tmp_path, mode="w:zst") as tar:
            # arcnameを相対パスで指定することで、解凍時にプロジェクトルートに展開されるようにする
            tar.add(str(target_dir_path), arcname=target_dir_path.relative_to(project_path))

        os.replace(tmp_path, cache_file)  # POSIX では原子的なリネーム
        tmp_path = None
        print("Cache saved successfully.")
        return 0
    except Exception as e:
        print(f"Failed to save cache: {e}", file=sys.stderr)
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        return 1

def restore_cache(project_path: Path, cache_dir: str, target_dir: str, cache_key: str, restore_keys: list[str] | None = None):
    """
    指定されたキャッシュキーに対応する圧縮ファイルを解凍し、プロジェクト内に復元します。
    """
    sanitized_key = sanitize_filename(cache_key)
    cache_root_dir = Path(cache_dir).resolve()
    # ディレクトリが存在しない場合は作成
    cache_root_dir.mkdir(parents=True, exist_ok=True)

    target_dir_path = project_path / target_dir

    # 1. プライマリキーでキャッシュを検索
    primary_cache_file = cache_root_dir / f"{sanitized_key}.tar.zst"
    
    cache_file_to_restore = None
    restored_key = None

    if primary_cache_file.exists():
        print(f"Found exact cache match for key: {cache_key}")
        cache_file_to_restore = primary_cache_file
        restored_key = cache_key
    else:
        # 2. フォールバックキーでキャッシュを検索
        print(f"Exact cache not found for key: {cache_key}. Searching with restore keys...")
        if restore_keys:
            best_match = None
            latest_mtime = 0
            
            all_cache_files = list(cache_root_dir.glob("*.tar.zst"))

            for key in restore_keys:
                sanitized_restore_key = sanitize_filename(key)
                print(f"Checking with restore key prefix: {key}")
                
                candidates = [f for f in all_cache_files if f.name.startswith(sanitized_restore_key)]
                
                if candidates:
                    for candidate in candidates:
                        mtime = candidate.stat().st_mtime
                        if mtime > latest_mtime:
                            latest_mtime = mtime
                            best_match = candidate
            
            if best_match:
                restored_key_name = best_match.name[:-len('.tar.zst')]
                print(f"Found best fallback cache match: {best_match.name}")
                cache_file_to_restore = best_match
                restored_key = restored_key_name

    if not cache_file_to_restore:
        print("No cache found for the given key or restore keys. Skipping cache restore.")
        return 0

    try:
        if target_dir_path.exists():
            # 展開先に既にディレクトリが存在する場合は、競合を避けるため事前に削除
            print(f"Removing existing target directory: {target_dir_path}")
            shutil.rmtree(target_dir_path, onerror=remove_readonly)

        print(f"Decompressing and extracting zstd archive from {cache_file_to_restore} using ThreadPoolExecutor for concurrent writes...")
        with tarfile.open(name=cache_file_to_restore, mode="r:zst") as tar, \
             ThreadPoolExecutor(max_workers=os.cpu_count() or 8) as executor:
            for member in tar:
                dest_path = project_path / member.name
                if member.isdir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    f_obj = tar.extractfile(member)
                    if f_obj:
                        data = f_obj.read()
                        executor.submit(write_file_concurrent, data, str(dest_path))

        print("Cache restored successfully.")
        return 0
    except Exception as e:
        print(f"Failed to restore cache: {e}", file=sys.stderr)
        return 1

def purge_cache(cache_dir: str, days: int) -> int:
    """
    指定された日数より古いキャッシュファイル (.tar.zst) を削除します。
    """
    cache_root_dir = Path(cache_dir).resolve()
    if not cache_root_dir.exists():
        print(f"Cache directory does not exist: {cache_root_dir}")
        return 0

    import time
    cutoff = time.time() - days * 86400
    deleted = 0

    for cache_file in cache_root_dir.glob("*.tar.zst"):
        if cache_file.stat().st_mtime < cutoff:
            print(f"Deleting: {cache_file}")
            cache_file.unlink()
            deleted += 1

    print(f"Purge complete: {deleted} file(s) deleted (older than {days} days).")
    return 0


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="Cache management script")
    parser.add_argument(
        "--project", default=".", help="Unity project path (default: current directory)"
    )
    parser.add_argument(
        "--cache-dir", required=True, help="Root directory for storing caches"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Save command
    parser_save = subparsers.add_parser("save", help="Save a directory to the cache")
    parser_save.add_argument(
        "--target-dir", required=True, help="Directory to cache"
    )
    parser_save.add_argument(
        "--cache-key", required=True, help="Unique key for the cache"
    )

    # Restore コマンド用の引数設定
    parser_restore = subparsers.add_parser("restore", help="Restore a directory from the cache")
    parser_restore.add_argument(
        "--target-dir", required=True, help="Directory to restore"
    )
    parser_restore.add_argument(
        "--cache-key", required=True, help="Primary key for the cache to restore"
    )
    parser_restore.add_argument(
        "--restore-keys", help="Comma-separated list of fallback keys for cache restore"
    )

    # Purge コマンド用の引数設定
    parser_purge = subparsers.add_parser("purge", help="Delete cache files older than N days")
    parser_purge.add_argument(
        "--days", type=int, default=14, help="Delete files older than this many days (default: 14)"
    )

    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    exit_code = 1

    # 指定されたサブコマンドに応じて処理を分岐
    if args.command == "save":
        exit_code = save_cache(project_path, args.cache_dir, args.target_dir, args.cache_key)
    elif args.command == "restore":
        restore_keys_list = args.restore_keys.split(',') if args.restore_keys else None
        exit_code = restore_cache(project_path, args.cache_dir, args.target_dir, args.cache_key, restore_keys_list)
    elif args.command == "purge":
        exit_code = purge_cache(args.cache_dir, args.days)

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
