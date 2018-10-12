const HtmlWebPackPlugin = require("html-webpack-plugin");

module.exports = {
    resolve: {
        // removes the need to add file extensions to the end of imports
        extensions: ["\0", ".webpack.js", ".web.js", ".js", ".jsx", ".scss"]
    },
    devServer: {
        // allows React-Router
        historyApiFallback: true
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader"
                }
            },
            {
                test: /\.html$/,
                use: [
                    {
                        loader: "html-loader"
                    }
                ]
            },
            // src: https://getbootstrap.com/docs/4.0/getting-started/webpack/
            {
                test: /\.(scss)$/,
                use: [{
                    loader: "style-loader" // inject CSS to page
                }, {
                    loader: "css-loader" // translates CSS into CommonJS modules
                }, {
                    loader: "postcss-loader", // Run post css actions
                    options: {
                        plugins: function() { // post css plugins, can be exported to postcss.config.js
                            return [
                                require("precss"),
                                require("autoprefixer")
                            ];
                        }
                    }
                }, {
                    loader: "sass-loader" // compiles Sass to CSS
                }]
            }
        ]
    },
    plugins: [
        new HtmlWebPackPlugin({
            template: "./src/index.html",
            filename: "./index.html"
        })
    ]
};
