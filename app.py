from flask import Flask, request, jsonify, send_from_directory
import pickle
import re
import os
import traceback
from nltk.stem import PorterStemmer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, 'vectorizer.pkl'), 'rb') as f:
    tfv = pickle.load(f)

ps = PorterStemmer()

STOPWORDS = {
    'the','a','an','and','or','but','if','while','is','are','was','were','be','been','to',
    'of','in','on','for','with','as','at','by','from','this','that','it','i','you','he',
    'she','they','we','my','your','our','their','me','him','her','them','so'
}

def clean_and_stem(text):
    text = re.sub(r'[^A-Za-z\s]', ' ', str(text))
    tokens = [t.strip() for t in text.lower().split() if t.strip()]
    tokens = [ps.stem(t) for t in tokens if t not in STOPWORDS and len(t) > 1]
    return ' '.join(tokens)

aspects_keywords = {
    'food': ['food','taste','flavor','dish','meal','menu','tasteful','tasty'],
    'service': ['service','staff','waiter','waitress','server','host','manager'],
    'speed': ['quick','slow','speed','time','wait','waited'],
    'hygiene': ['hygiene','clean','dirty','sanitary','unclean','hygienic','cleanliness'],
    'ambience': ['ambience','ambiance','atmosphere','music','decor','lighting'],
    'price': ['price','cost','expensive','cheap','value','worth']
}

aspects_regex = {
    asp: re.compile(r'\b(' + r'|'.join(map(re.escape, kws)) + r')\b', flags=re.IGNORECASE)
    for asp, kws in aspects_keywords.items()
}

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
    return [p.strip() for p in parts if p.strip()]

def analyze_text(text):
    cleaned = clean_and_stem(text)
    vec = tfv.transform([cleaned]).toarray()
    pred = int(model.predict(vec)[0])
    prob = None
    if hasattr(model, "predict_proba"):
        try:
            prob = float(model.predict_proba(vec).max())
        except:
            prob = None

    aspect_results = {}
    sentences = split_sentences(text)

    for s in sentences:
        for asp, rx in aspects_regex.items():
            if rx.search(s):
                s_clean = clean_and_stem(s)
                v = tfv.transform([s_clean]).toarray()
                try:
                    p = int(model.predict(v)[0])
                except:
                    p = pred
                p_prob = None
                if hasattr(model, "predict_proba"):
                    try:
                        p_prob = float(model.predict_proba(v).max())
                    except:
                        p_prob = None
                aspect_results.setdefault(asp, []).append({
                    "sentence": s,
                    "pred": p,
                    "probability": p_prob
                })

    return {
        "prediction": pred,
        "probability": prob,
        "aspects": aspect_results
    }

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        if not data or 'text' not in data:
            return jsonify({"error": True, "message": "JSON must include 'text' field"}), 400
        text = str(data['text']).strip()
        if not text:
            return jsonify({"error": True, "message": "Empty text provided"}), 400
        result = analyze_text(text)
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": True,
            "exception_type": type(e).__name__,
            "exception_str": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)