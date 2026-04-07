import * as exec from '@actions/exec';
import { join } from 'path';

export function getScriptPath() {
  return join(__dirname, '..', '..', '..', 'scripts', 'cache.py');
}

export function getCacheDir({ useLfs = false } = {}) {
  const dir = useLfs
    ? (process.env.LFS_CACHE_DIR || process.env.PERSISTENT_CACHE_DIR)
    : process.env.PERSISTENT_CACHE_DIR;
  if (!dir) {
    throw new Error(
      useLfs
        ? 'LFS_CACHE_DIR と PERSISTENT_CACHE_DIR がどちらも未設定です'
        : 'PERSISTENT_CACHE_DIR が未設定です'
    );
  }
  return dir;
}

export async function restore({ cacheDir, targetDir, cacheKey, restoreKeys }) {
  const args = [
    getScriptPath(),
    '--cache-dir', cacheDir,
    'restore',
    '--target-dir', targetDir,
    '--cache-key', cacheKey,
  ];
  if (restoreKeys) args.push('--restore-keys', restoreKeys);
  await exec.exec('python', args);
}

export async function save({ cacheDir, targetDir, cacheKey }) {
  await exec.exec('python', [
    getScriptPath(),
    '--cache-dir', cacheDir,
    'save',
    '--target-dir', targetDir,
    '--cache-key', cacheKey,
  ]);
}
