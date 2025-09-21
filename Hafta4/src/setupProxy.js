const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'https://test.divvydrive.com',
      changeOrigin: true,
      secure: true,
      timeout: 300000, 
      proxyTimeout: 300000, 
      pathRewrite: {
        '^/api': '/Test/Staj'
      },
      headers: {
        'Authorization': `Basic ${Buffer.from('NDSServis:ca5094ef-eae0-4bd5-a94a-14db3b8f3950').toString('base64')}`
      },
      onProxyReq: function(proxyReq, req, res) {
        proxyReq.setTimeout(300000); 
        
        console.log(`[PROXY] ${req.method} ${req.url} -> ${proxyReq.protocol}//${proxyReq.host}${proxyReq.path}`);
        
        if (req.url.includes('DosyaParcalariYukle') || req.url.includes('DosyaDirektYukle')) {
          proxyReq.setHeader('Connection', 'keep-alive');
          proxyReq.setHeader('Keep-Alive', 'timeout=300, max=1000');
        }
      },
      onProxyRes: function(proxyRes, req, res) {
        res.header('Access-Control-Allow-Origin', '*');
        res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
        res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Length, X-Requested-With');
        
        console.log(`[PROXY] Response: ${proxyRes.statusCode} for ${req.url}`);
      },
      onError: function(err, req, res) {
        console.error('[PROXY] Error:', err.message);
        
        if (err.code === 'ETIMEDOUT' || err.code === 'ESOCKETTIMEDOUT') {
          res.status(408).json({ 
            error: 'Upload timeout', 
            message: 'Dosya yükleme zaman aşımına uğradı. Lütfen daha küçük parçalar halinde deneyin.' 
          });
        } else {
          res.status(500).json({ error: 'Proxy error', message: err.message });
        }
      }
    })
  );
};