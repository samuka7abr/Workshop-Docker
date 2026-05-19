const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Olá, Docker! Aplicação Node.js rodando no container.');
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

app.get('/api/info', (req, res) => {
  res.json({
    app: 'workshop-docker-app',
    node: process.version,
    platform: process.platform,
    port: PORT,
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Servidor ouvindo em http://0.0.0.0:${PORT}`);
});
