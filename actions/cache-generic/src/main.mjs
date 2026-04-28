import * as core from '@actions/core';
import { getCacheDir, restore } from '../../_shared/cache-action.mjs';

;(async () => {
  try {
    const targetDir = core.getInput('target-dir', { required: true });
    const cacheKey  = core.getInput('cache-key',   { required: true });
    const restoreKeys = core.getInput('restore-keys') || undefined;
    const cacheDir  = getCacheDir();

    await restore({ cacheDir, targetDir, cacheKey, restoreKeys });
  } catch (error) {
    core.setFailed(error.message);
  }
})();
