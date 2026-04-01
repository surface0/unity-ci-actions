import * as core from '@actions/core'
import { getCacheDir, restore } from '../../_shared/cache-action.mjs'

;(async () => {
  try {
    const cacheKey = core.getInput('cache-key', { required: true })
    // LFS_CACHE_DIR 未設定時は PERSISTENT_CACHE_DIR にフォールバック
    const cacheDir = getCacheDir({ useLfs: true })

    // restore-keys に同じキーを渡してプレフィックス一致フォールバックを有効にする
    await restore({ cacheDir, targetDir: '.git/lfs', cacheKey, restoreKeys: cacheKey })
  } catch (error) {
    core.setFailed(error.message)
  }
})()