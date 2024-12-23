var path = require('path')
var config = require('../config')
const MiniCssExtractPlugin = require("mini-css-extract-plugin");


exports.resolveFromRoot = function(dir) {
  return path.join(__dirname, "..", dir);
}

exports.assetsPath = function (_path) {
  var assetsSubDirectory = process.env.NODE_ENV === 'production'
    ? config.build.assetsSubDirectory
    : config.dev.assetsSubDirectory
  return path.posix.join(assetsSubDirectory, _path)
}

exports.cssLoaders = function (options) {
  options = options || {}
  // generate loader string to be used with extract text plugin
  function generateLoaders (loaders) {
    var sourceLoader = loaders.map(function (loader) {
      if (typeof loader === 'string') {
        var extraParamChar
        if (/\?/.test(loader)) {
          loader = loader.replace(/\?/, '-loader?')
          extraParamChar = '&'
        } else {
          loader = loader + '-loader'
          extraParamChar = '?'
        }
        return loader + (options.sourceMap ? extraParamChar + 'sourceMap' : '')
      } else {
        return loader
      }
    })
    
    if (typeof loader === 'string') {
      // Extract CSS when that option is specified
      // (which is the case during production build)
      if (options.extract) {
        return ExtractTextPlugin.extract({
          use: sourceLoader,
          fallback: 'vue-style-loader'
        })
      }
    }
    return ['vue-style-loader', MiniCssExtractPlugin.loader].concat(sourceLoader)
  }

  // http://vuejs.github.io/vue-loader/en/configurations/extract-css.html
  return {
    css: generateLoaders(['css']),
    postcss: generateLoaders(['css']),
    less: generateLoaders(['css', 'less']),
    sass: generateLoaders(['css', 'sass?indentedSyntax']),
    scss: generateLoaders(['css', {
        loader: 'sass-loader',
        options: {
            includePaths: [path.resolve('node_modules/foundation-sites/scss')]
        }
    }]),
    stylus: generateLoaders(['css', 'stylus']),
    styl: generateLoaders(['css', 'stylus'])
  }
}

// Generate loaders for standalone style files (outside of .vue)
exports.styleLoaders = function (options) {
  var output = []
  var loaders = exports.cssLoaders(options)
  for (var extension in loaders) {
    var loader = loaders[extension]
    output.push({
      test: new RegExp('\\.' + extension + '$'),
      use: loader
    })
  }
  return output
}
