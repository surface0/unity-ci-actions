import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'

function actionBundle(name, entryName) {
  return {
    input: `actions/${name}/src/${entryName}.mjs`,
    output: {
      file: `actions/${name}/dist/${entryName}.js`,
      format: 'cjs',
    },
    plugins: [resolve({ preferBuiltins: true }), commonjs()],
  }
}

const cacheActions = ['cache-generic', 'cache-lfs', 'cache-library']

export default cacheActions.flatMap(name => [
  actionBundle(name, 'main'),
  actionBundle(name, 'post'),
])
