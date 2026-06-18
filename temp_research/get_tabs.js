const http = require('http');

http.get('http://localhost:9222/json', (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    try {
      const json = JSON.parse(data);
      console.log(JSON.stringify(json, null, 2));
    } catch (e) {
      console.error("Failed to parse JSON:", e.message);
      console.log(data);
    }
  });
}).on('error', (err) => {
  console.error("Error connecting to debugging port:", err);
});
