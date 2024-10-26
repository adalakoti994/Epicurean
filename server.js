const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { MetaAI } = require('meta-ai-api');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(bodyParser.json());

app.post('/api/metaai', async (req, res) => {
  const { question } = req.body;

  const ai = new MetaAI();
  try {
    const response = await ai.prompt(message=question);
    res.json({ answer: response });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred while contacting the MetaAI API.' });
  }
});
app.use(express.static('public'));


app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
