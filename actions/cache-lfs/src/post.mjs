import * as core from '@actions/core';
import { getCacheDir, save } from '../../_shared/cache-action.mjs';

;(async () => {
  try {
    if (core.getInput('skip-save') === 'true') {
      core.info('skip-save が true のためセーブをスキップします');
      return;
    }

    const cacheKey = core.getInput('cache-key', { required: true });
    const cacheDir = getCacheDir({ useLfs: true });

    await save({ cacheDir, targetDir: '.git/lfs', cacheKey });
  } catch (error) {
    core.setFailed(error.message);
  }
})();
