from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import pickle
import os

app = Flask(__name__)
CORS(app)

# Try to import RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Draw
    import base64
    from io import BytesIO
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("RDKit not available - using mock mode")

# Try to import sklearn
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

MODELS_MULTI_PATH = "models_multi.pkl"
TARGET_COLS = [
    "NR-AR", "NR-AR-LBD", "NR-AhR", "NR-Aromatase",
    "NR-ER", "NR-ER-LBD", "NR-PPAR-gamma",
    "SR-ARE", "SR-ATAD5", "SR-HSE", "SR-MMP", "SR-p53"
]

models_bundle = None  # dict: models dict, meta dict, or legacy single clf

def smiles_to_fingerprint(smiles):
    """Convert SMILES to Morgan fingerprint."""
    if not RDKIT_AVAILABLE:
        np.random.seed(hash(smiles) % 2**32)
        return np.random.randint(0, 2, 2048)
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
    return np.array(fp)

def get_molecule_image(smiles):
    """Generate molecule image as base64."""
    if not RDKIT_AVAILABLE:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        img = Draw.MolToImage(mol, size=(300, 200))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception:
        return None

def _tree_uncertainty(clf, fp):
    """Std dev of positive-class probability across trees (epistemic spread)."""
    probs = []
    for tree in clf.estimators_:
        probs.append(tree.predict_proba(fp.reshape(1, -1))[0, 1])
    return float(np.std(probs)) if probs else 0.0

def _mean_importances(models_dict):
    """Average feature importances across trained assay models."""
    imps = []
    for clf in models_dict.values():
        if hasattr(clf, "feature_importances_"):
            imps.append(clf.feature_importances_)
    if not imps:
        return np.zeros(2048)
    return np.mean(np.stack(imps, axis=0), axis=0)

def train_model():
    """Train per-assay models on Tox21 CSV, or fall back to mock."""
    global models_bundle

    tox21_path = "tox21.csv"
    if os.path.exists(tox21_path) and RDKIT_AVAILABLE and SKLEARN_AVAILABLE:
        print("Training on Tox21 dataset (multi-target)...")
        df = pd.read_csv(tox21_path)

        fps = []
        valid_idx = []
        for i, smi in enumerate(df["smiles"]):
            fp = smiles_to_fingerprint(str(smi))
            if fp is not None:
                fps.append(fp)
                valid_idx.append(i)

        X = np.array(fps)
        valid_idx = np.array(valid_idx)

        models_dict = {}
        meta_dict = {}

        for target in TARGET_COLS:
            if target not in df.columns:
                continue
            y_series = df[target].iloc[valid_idx]
            mask = ~y_series.isna()
            if mask.sum() < 80:
                continue
            y = y_series[mask].fillna(0).astype(int)
            X_t = X[mask.values]
            if len(np.unique(y)) < 2:
                continue

            X_train, X_test, y_train, y_test = train_test_split(
                X_t, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
            )
            clf = RandomForestClassifier(
                n_estimators=100, n_jobs=-1, random_state=42, class_weight="balanced"
            )
            clf.fit(X_train, y_train)
            try:
                auc = roc_auc_score(y_test, clf.predict_proba(X_test)[:, 1])
            except Exception:
                auc = 0.5
            models_dict[target] = clf
            meta_dict[target] = {
                "n_samples": int(len(y)),
                "n_positive": int(y.sum()),
                "auc_holdout": float(auc),
            }
            print(f"  {target}: n={len(y)} AUC≈{auc:.3f}")

        if models_dict:
            bundle = {"type": "multi", "models": models_dict, "meta": meta_dict}
            models_bundle = bundle
            with open(MODELS_MULTI_PATH, "wb") as f:
                pickle.dump(bundle, f)
            print(f"Saved multi-target bundle ({len(models_dict)} assays).")
            return

    print("Using mock model (add tox21.csv to use real data)")
    if SKLEARN_AVAILABLE:
        X_dummy = np.random.randint(0, 2, (500, 2048))
        y_dummy = np.random.randint(0, 2, 500)
        clf = RandomForestClassifier(n_estimators=10, random_state=42)
        clf.fit(X_dummy, y_dummy)
        models_bundle = {"type": "legacy", "models": {"NR-AR": clf}, "meta": {}}

def predict_toxicity(smiles):
    """Predict toxicity scores per assay; return uncertainty when models exist."""
    fp = smiles_to_fingerprint(smiles)
    if fp is None:
        return None, None, None, None, None

    results = {}
    assay_uncertainty = {}
    feature_importance = []

    if models_bundle is None or not SKLEARN_AVAILABLE:
        np.random.seed(hash(smiles) % 2**32)
        for col in TARGET_COLS:
            results[col] = float(np.random.uniform(0, 1))
        u = {col: float(np.random.uniform(0.02, 0.15)) for col in TARGET_COLS}
        feature_importance = [
            {"feature": f"Bit {i}", "importance": float(np.random.uniform(0, 0.1))}
            for i in range(10)
        ]
        return results, feature_importance, u, {}, []

    btype = models_bundle.get("type")
    models_dict = models_bundle["models"]
    meta = models_bundle.get("meta", {})

    if btype == "multi":
        importances = _mean_importances(models_dict)
        top_indices = np.argsort(importances)[::-1][:10]
        feature_importance = [
            {"feature": f"Bit {i}", "importance": float(importances[i])}
            for i in top_indices
        ]

        for target in TARGET_COLS:
            if target in models_dict:
                clf = models_dict[target]
                p = clf.predict_proba(fp.reshape(1, -1))[0, 1]
                results[target] = float(np.clip(p, 0, 1))
                assay_uncertainty[target] = _tree_uncertainty(clf, fp)
            else:
                np.random.seed((hash(smiles) + hash(target)) % 2**32)
                results[target] = float(np.random.uniform(0.1, 0.9))
                assay_uncertainty[target] = 0.2
    else:
        clf = list(models_dict.values())[0]
        prob = clf.predict_proba(fp.reshape(1, -1))[0][1]
        importances = clf.feature_importances_
        top_indices = np.argsort(importances)[::-1][:10]
        feature_importance = [
            {"feature": f"Bit {i}", "importance": float(importances[i])}
            for i in top_indices
        ]
        base_scores = {
            "NR-AR": prob,
            "NR-AR-LBD": min(1, prob * 0.9 + 0.05),
            "NR-AhR": min(1, prob * 1.1 - 0.05),
            "NR-Aromatase": min(1, prob * 0.8 + 0.1),
            "NR-ER": min(1, prob * 0.95),
            "NR-ER-LBD": min(1, prob * 0.85 + 0.05),
            "NR-PPAR-gamma": min(1, prob * 0.7 + 0.1),
            "SR-ARE": min(1, prob * 1.05 - 0.02),
            "SR-ATAD5": min(1, prob * 0.9),
            "SR-HSE": min(1, prob * 0.75 + 0.15),
            "SR-MMP": min(1, prob * 1.2 - 0.1),
            "SR-p53": min(1, prob * 0.95 + 0.02),
        }
        results = {k: max(0, min(1, float(v))) for k, v in base_scores.items()}
        u0 = _tree_uncertainty(clf, fp)
        assay_uncertainty = {k: float(u0) for k in TARGET_COLS}

    low_confidence = []
    for t in TARGET_COLS:
        u = assay_uncertainty.get(t, 0)
        ntrain = meta.get(t, {}).get("n_samples", 9999)
        if u > 0.14 or ntrain < 200:
            low_confidence.append(t)

    return results, feature_importance, assay_uncertainty, meta, low_confidence

@app.route("/", methods=["GET"])
@app.route("/docs", methods=["GET"])
def api_docs():
    return jsonify({
        "name": "ToxScan API",
        "version": "1.1",
        "endpoints": {
            "GET /health": {
                "returns": "status, rdkit, model_loaded, multi_target, targets_trained",
            },
            "GET /docs": "This document.",
            "POST /predict": {
                "body": {"smiles": "string"},
                "returns": {
                    "smiles": "string",
                    "overall_risk": "float 0-1",
                    "assay_scores": "dict assay -> float",
                    "assay_uncertainty": "dict assay -> float (tree disagreement)",
                    "assay_train_meta": "per-assay training stats when available",
                    "low_confidence_assays": "list of assay keys",
                    "feature_importance": "list of {feature, importance}",
                    "mol_image": "base64 PNG or null",
                    "risk_level": "Low|Medium|High",
                },
            },
        },
        "disclaimer": "Research / demo only — not for clinical or regulatory decisions.",
    })

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json or {}
    smiles = data.get("smiles", "").strip()
    if not smiles:
        return jsonify({"error": "No SMILES provided"}), 400

    scores, feature_importance, assay_uncertainty, train_meta, low_confidence = predict_toxicity(smiles)
    if scores is None:
        return jsonify({"error": "Invalid SMILES string"}), 400

    overall_risk = float(np.mean(list(scores.values())))
    mol_image = get_molecule_image(smiles)

    out = {
        "smiles": smiles,
        "overall_risk": overall_risk,
        "assay_scores": scores,
        "feature_importance": feature_importance,
        "mol_image": mol_image,
        "risk_level": "High" if overall_risk > 0.6 else "Medium" if overall_risk > 0.3 else "Low",
        "model_version": "multi_target_v1" if models_bundle and models_bundle.get("type") == "multi" else "legacy_or_mock",
    }
    if assay_uncertainty:
        out["assay_uncertainty"] = assay_uncertainty
    if train_meta:
        out["assay_train_meta"] = train_meta
    if low_confidence:
        out["low_confidence_assays"] = low_confidence

    return jsonify(out)

@app.route("/health", methods=["GET"])
def health():
    multi = bool(models_bundle and models_bundle.get("type") == "multi")
    n_targets = 0
    if models_bundle and isinstance(models_bundle.get("models"), dict):
        n_targets = len(models_bundle["models"])
    return jsonify({
        "status": "ok",
        "rdkit": RDKIT_AVAILABLE,
        "model_loaded": models_bundle is not None,
        "multi_target": multi,
        "targets_trained": n_targets,
    })

if __name__ == "__main__":
    train_model()
    app.run(debug=True, port=5000)
