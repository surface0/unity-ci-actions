import * as core from '@actions/core';
import { getCacheDir, save } from '../../_shared/cache-action.mjs';

;(async () => {
  try {
    if (core.getInput('skip-save') === 'true') {
      core.info('skip-save が true のためセーブをスキップします');
      return;
    }

    const targetDir = core.getInput('target-dir', { required: true });
    const cacheKey  = core.getInput('cache-key',   { required: true });
    const cacheDir  = getCacheDir();

    await save({ cacheDir, targetDir, cacheKey });
  } catch (error) {
    core.setFailed(error.message);
  }
})();
