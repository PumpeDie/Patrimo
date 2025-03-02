import dotenv from 'dotenv';
import express from 'express';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Deactivate ESLint advertissement for this line
// eslint-disable-next-line no-console
app.get('/', (req, res) => {
  res.send('Welcome on Patrimo!');
});

app.listen(port, () => {
  console.log(`Backend app listening at ${port}`);
});
