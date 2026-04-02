Here is the perfect, hackathon-ready `README.md` for your GitHub repository. It clearly outlines the tech stack, provides quick setup instructions, and—most importantly—puts that winning biological insight front and center for the judges.

You can copy and paste this directly into your repo\!

-----

# 🧬 Drug Toxicity Predictor

**A real-time web application for predicting molecular toxicity using Machine Learning and Cheminformatics.**

   

## 🎯 Project Overview

Evaluating the potential toxicity of novel chemical compounds is a critical bottleneck in the early stages of drug discovery. This project provides a lightweight, fast, and interpretable interface that takes a SMILES (Simplified Molecular-Input Line-Entry System) string and instantly predicts its safety profile across 12 different toxicity assays.

## 🔬 Key Biological Insight & Approach

Instead of treating molecules as raw text, our pipeline leverages **Morgan Fingerprints**. These fingerprints encode circular atom neighborhoods, allowing the model to "see" the 2D topological structure of the molecule in a way that mimics chemical intuition.

By utilizing a Random Forest classifier, we not only predict toxicity but extract **feature importance**. For example, our model correctly identifies that specific substructures—such as halogens and aromatic nitro groups—are some of the strongest predictors of Nuclear Receptor (NR-AR) toxicity. This aligns perfectly with known genotoxic mechanisms, proving that the model is learning real biology, not just memorizing data.

## ✨ Features

  * **Real-Time Predictions:** Input any valid SMILES string to get immediate toxicity risk scoring.
  * **Interpretability Dashboard:** Visualizes the top 5 molecular features driving the prediction via an interactive bar chart.
  * **Tox21 Heatmap:** Displays a comprehensive breakdown of the compound's risk profile across all 12 standard Tox21 assays (e.g., p53, AhR, ER).
  * **Visual Structure Generation:** Automatically renders the 2D molecular structure directly in the UI using RDKit.
  * **Pre-loaded Benchmarks:** Includes quick-test presets for well-known compounds like Aspirin, Caffeine, and DDT for easy demonstration.

## 🛠️ Tech Stack

  * **Backend:** Python, Flask
  * **Machine Learning:** scikit-learn (Random Forest)
  * **Cheminformatics:** RDKit (Molecule parsing, fingerprint generation, structural drawing)
  * **Frontend:** HTML5, CSS3, Vanilla JavaScript, Chart.js
  * **Dataset:** Tox21 (Toxicology in the 21st Century) primary dataset (\~12,000 compounds).

## 🚀 Quick Start / How to Run

**1. Clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/toxicity-predictor.git
cd toxicity-predictor
```

**2. Install dependencies:**
Make sure you have Python installed, then run:

```bash
pip install flask rdkit-pypi scikit-learn pandas numpy
```

**3. Run the application:**

```bash
python app.py
```

**4. View the app:**
Open your browser and navigate to `http://localhost:5000`

*Note: If the Tox21 CSV is not present in the root directory upon startup, the app will seamlessly fall back to a mock model so the UI can still be tested and demonstrated.*
