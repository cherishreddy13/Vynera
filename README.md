# VYNERA AI – Companion Chatbot

A self-hosted, psychologically-sound AI companion. No external APIs. Runs on your own VPS.

---

## Architecture Decision: GRU + Attention

**Chosen:** Bidirectional GRU Encoder + Bahdanau Attention + GRU Decoder (seq2seq)

| Criterion | Score | Reason |
|-----------|-------|--------|
| Dataset size (50k–150k) | ✅ | GRU trains stably on mid-size data; transformers need 500k+ |
| CPU inference speed | ✅ | ~0.4–0.9s/response (GRU has 2 gates vs LSTM's 3) |
| Nightly fine-tuning | ✅ | Stable gradients, no vanishing, safe on 50–200 pairs |
| Memory | ✅ | ~14.7M params, fits in 2GB RAM |
| Psychological coherence | ✅ | Attention over encoder lets decoder focus on emotional words |

**Specs:** 2-layer BiGRU encoder (hidden=512), 2-layer GRU decoder (hidden=512), embed=256, vocab=8000.  
**Parameters:** ~14.7M  
**Inference:** 0.4–0.9s CPU, ~0.1s GPU

---

## Quick Start

### 1. Install dependencies

```bash
# Python 3.10+ required
pip install -r requirements.txt

# MongoDB (Ubuntu/Debian)
sudo apt install -y mongodb
sudo systemctl start mongodb
```

### 2. Configure environment

```bash
cp .env.template .env
# Edit .env and set SECRET_KEY and MONGO_URI
```

### 3. Download datasets

```bash
# EmpatheticDialogues
git clone https://github.com/facebookresearch/EmpatheticDialogues.git data/EmpatheticDialogues

# DailyDialog
wget http://yanran.li/files/ijcnlp_dailydialog.zip -P data/
cd data && unzip ijcnlp_dailydialog.zip && cd ..

# BlendedSkillTalk + CounselChat + WikiDialog (via HuggingFace)
pip install datasets
python -c "
from datasets import load_dataset
load_dataset('blended_skill_talk')['train'].to_json('data/bst_train.jsonl')
load_dataset('nbertagnolli/counsel-chat')['train'].to_json('data/counsel.jsonl')
"
```

### 4. Prepare training data

```bash
python prepare_data.py
# Creates data/train.jsonl with weighted, merged dataset
```

### 5. Train the model

```bash
# CPU training (~6-12 hours for 20 epochs on 100k pairs):
python -m model.train --epochs 20 --batch-size 32

# GPU training (~1-2 hours):
python -m model.train --epochs 20 --batch-size 64 --device cuda

# Resume training:
python -m model.train --resume
```

### 6. Run the app

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
```

Open `http://localhost:8000` → Sign up → Start chatting.

---

## MongoDB Indexes (auto-created on startup)

The app automatically creates these indexes:
- `users`: unique on `email`, `username`
- `conversations`: compound `(user_id, created_at)`
- `memories`: compound `(user_id, key)`
- `feedback`: `(user_id, used_in_training)` + `created_at`

To verify manually:
```bash
mongosh vynera --eval "db.users.getIndexes()"
```

---

## Self-Learning Loop (Nightly Fine-Tuning)

1. **Collection**: Every 👍/👎 feedback from users is stored in the `feedback` collection with `used_in_training: false`.
2. **Trigger**: At 3 AM (configurable in `.env` via `NIGHTLY_FINETUNE_HOUR`), APScheduler fires `run_nightly_self_learn()`.
3. **Threshold**: Runs only if `>= 50` unprocessed feedback items exist (configurable: `FEEDBACK_BATCH_THRESHOLD`).
4. **Positive pairs**: 👍 feedback → `(user_message, bot_message)` treated as gold training pairs.
5. **Negative logging**: 👎 responses are logged to `data/negative_feedback.jsonl` for future RLHF-style filtering (not trained on directly in MVP).
6. **Fine-tuning**: `FINETUNE_EPOCHS=2` epochs, `lr=1e-4` (low to prevent catastrophic forgetting). Encoder embeddings frozen to preserve base vocabulary.
7. **Backup**: Pre-fine-tune checkpoint saved as `models/latest_pre_finetune.pt` before each run.
8. **Marking**: All processed feedback marked `used_in_training: true`.

---

## PyTorch Installation Notes

```bash
# CPU only (smaller, faster install):
pip install torch --index-url https://download.pytorch.org/whl/cpu

# CUDA 12.1 (if you have an NVIDIA GPU):
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Verify:
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

---

## VPS Deployment (Production)

```bash
# Use gunicorn + uvicorn workers
pip install gunicorn

gunicorn app:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 2 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log

# With nginx reverse proxy (recommended):
# Point nginx to localhost:8000, enable WebSocket upgrade headers.
```

**nginx WebSocket config snippet:**
```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

---

## 8-bit Quantisation (CPU memory saving)

After training, quantise the model for faster CPU inference:

```python
import torch
from model.core import VyneraModel, WordTokenizer

tokenizer = WordTokenizer.load('models/tokenizer.json')
model = VyneraModel(vocab_size=len(tokenizer))
ckpt = torch.load('models/latest.pt', map_location='cpu')
model.load_state_dict(ckpt['model_state_dict'])

# Dynamic quantisation (no retraining needed)
quantised = torch.quantization.quantize_dynamic(
    model, {torch.nn.GRU, torch.nn.Linear}, dtype=torch.qint8
)
torch.save({'model_state_dict': quantised.state_dict()}, 'models/quantised.pt')
print("Quantised model saved.")
```

Then set `MODEL_PATH=models/quantised.pt` in `.env`.

---

## Folder Structure

```
companion_chatbot/
├── app.py                    # FastAPI app, all routes, WebSocket
├── config.py                 # Settings from .env
├── requirements.txt
├── prepare_data.py           # Merge datasets → data/train.jsonl
├── .env.template             # Copy to .env
├── model/
│   ├── core.py               # GRU+Attention model, tokenizer, generation
│   ├── train.py              # Full training script
│   └── self_learn.py         # Nightly fine-tuning
├── db/
│   └── mongo.py              # Async Motor CRUD
├── utils/
│   ├── sentiment.py          # Emotion detection (lexicon)
│   ├── memory.py             # Fact extraction & retrieval
│   └── safety.py             # Crisis detection, safety rules
├── static/js/
│   └── chat.js               # WebSocket client, UI logic
├── templates/                # 7 HTML pages with internal CSS
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── history.html
│   └── chat.html
├── data/                     # Training datasets go here
└── models/                   # Saved checkpoints
```

---

## Crisis Hotline Configuration

Edit `.env`:
```
CRISIS_HOTLINE=iCall: 9152987821
CRISIS_HOTLINE_URL=https://icallhelpline.org
```

Replace with your country's relevant crisis helpline. The bot will display this automatically whenever crisis language is detected.