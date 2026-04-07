import * as core from '@actions/core';
import { getCacheDir, save } from '../../_shared/cache-action.mjs';

;(async () => {
  try {
    if (core.getInput('skip-save') === 'true') {
      core.info('skip-save が true のためセーブをスキップします');
      return;
    }

    const unityVersion = core.getInput('unity-version', { required: true });
    const cacheDir = getCacheDir();

    const repo   = (process.env.GITHUB_REPOSITORY ?? '').split('/')[1] ?? 'unknown';
    const branch = process.env.GITHUB_REF_NAME ?? 'unknown';
    const cacheKey = `${repo}-Library-${unityVersion}-${branch}`;

    await save({ cacheDir, targetDir: 'Library', cacheKey });
  } catch (error) {
    core.setFailed(error.message);
  }
})();
