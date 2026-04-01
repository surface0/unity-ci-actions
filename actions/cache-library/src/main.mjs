import * as core from '@actions/core'
import { getCacheDir, restore } from '../../_shared/cache-action.mjs'

;(async () => {
  try {
    const unityVersion = core.getInput('unity-version', { required: true })
    const cacheDir = getCacheDir()

    // キャッシュキー形式: {repo}-Library-{unity-version}-{branch}
    // restore-keys:     {repo}-Library-{unity-version}-  ← バージョンが同じ別ブランチにフォールバック
    const repo   = (process.env.GITHUB_REPOSITORY ?? '').split('/')[1] ?? 'unknown'
    const branch = process.env.GITHUB_REF_NAME ?? 'unknown'
    const cacheKey    = `${repo}-Library-${unityVersion}-${branch}`
    const restoreKeys = `${repo}-Library-${unityVersion}-`

    await restore({ cacheDir, targetDir: 'Library', cacheKey, restoreKeys })
  } catch (error) {
    core.setFailed(error.message)
  }
})()