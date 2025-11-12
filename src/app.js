const express = require('express');
const bodyParser = require('body-parser');
const { initDb, insertEvent, getAllEvents, queryEventsForUser } = require('./db');
const { scoreEvent } = require('./model');

const app = express();
app.use(bodyParser.json());
initDb();

app.get('/', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

app.post('/events', (req, res) => {
  const data = req.body;
  const required = ['user_id', 'ip', 'timestamp', 'success', 'location', 'user_agent'];
  for (const r of required) {
    if (!(r in data)) return res.status(400).json({ error: `missing field ${r}` });
  }

  try {
    insertEvent(data);
  } catch (err) {
    return res.status(500).json({ error: 'db insert failed', detail: String(err) });
  }

  const { score, reasons } = scoreEvent(data);
  const alert = score >= 0.5;
  return res.status(201).json({ stored: true, score, reasons, alert });
});

app.get('/alerts', (req, res) => {
  const events = getAllEvents(1000);
  const alerts = events
    .map(e => {
      const { score, reasons } = scoreEvent(e);
      if (score >= 0.5) return { ...e, score, reasons };
      return null;
    })
    .filter(Boolean);
  res.json({ alerts });
});

app.get('/users/:user_id/summary', (req, res) => {
  const user_id = req.params.user_id;
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const events = queryEventsForUser(user_id, since);
  const total = events.length;
  const failures = events.filter(e => !Boolean(e.success)).length;
  const last_event = events.length ? events[0] : null;
  res.json({ user_id, events_last_24h: total, failures_last_24h: failures, last_event });
});

const PORT = 5000;
app.listen(PORT, () => console.log(`Server running at http://127.0.0.1:${PORT}`));
