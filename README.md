# ToxScan — Tox21-style toxicity from SMILES

ToxScan predicts toxicity risk across 12 Tox21 assays from a molecule’s SMILES using Morgan fingerprints and random forests trained on public Tox21-style data.

For any compound, the highest-scoring assay drives the generated insight and the Low/Medium/High risk band.

**This is a research and hackathon demo only—not for clinical or regulatory use.**

---

## Quick start (local)

1. **Backend** (from `backend/`):

   ```bash
   pip install -r requirements.txt
   python app.py
   ```

   Place `tox21.csv` in `backend/` to train per-assay models (writes `models_multi.pkl` on success).

2. **Frontend**: open `frontend/index.html` in a browser, or serve the folder with any static server.

   Default API base: `http://localhost:5000`.

---

## Hosted demo — point the UI at your API

If the HTML is on GitHub Pages (or any static host) and the API elsewhere:

- **One-off (shareable link):** add a query parameter, for example:

  `https://yoursite.github.io/toxscan/index.html?api=https://your-api.onrender.com`

  The app stores that base in `localStorage` for later visits (same browser).

- **Override again:** visit with a new `?api=...` or clear site data for the page.

Ensure the backend allows CORS from your frontend origin (`flask-cors` is enabled broadly in `app.py`; tighten for production if needed).

### Backend hosting (examples)

- [Render](https://render.com), [Railway](https://railway.app), [Fly.io](https://fly.io): deploy the Flask app; set start command to run `app.py` (or `gunicorn` in production).
- **Quick tunnel for judging:** run `python app.py` locally and expose with [ngrok](https://ngrok.com) (`ngrok http 5000`), then open the frontend with `?api=https://xxxx.ngrok-free.app`.

---

## API (for tooling)

- `GET /` or `GET /docs` — JSON field reference  
- `GET /health` — status, RDKit, `multi_target`, `targets_trained`  
- `POST /predict` — body `{"smiles":"..."}`

---

## Portfolio screenshot / GIF

Step-by-step: **[docs/SCREENSHOT.md](docs/SCREENSHOT.md)**  
After you save `docs/demo.gif` (or `docs/demo.png`), you can embed it in this README:

```markdown
![ToxScan demo](docs/demo.gif)
```

---

## Tech stack

Flask · RDKit · scikit-learn · vanilla JS + canvas (no chart library on the critical path)
