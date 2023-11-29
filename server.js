//get/post/put

const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// GET request
app.get('/api/data', (req, res) => {
  // Your logic to handle the GET request
  res.json({ message: 'This is a GET request' });
});

// POST request
app.post('/api/data', (req, res) => {
  // Your logic to handle the POST request
  const requestData = req.body;
  res.json({ message: 'This is a POST request', data: requestData });
});

// PUT request
app.put('/api/data/:id', (req, res) => {
  // Your logic to handle the PUT request
  const id = req.params.id;
  const requestData = req.body;
  res.json({ message: `This is a PUT request for ID: ${id}`, data: requestData });
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
