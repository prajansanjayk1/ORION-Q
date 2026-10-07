import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import shutil
import os

def update_paragraph_preserve_formatting(p, new_text):
    if not p.runs:
        p.text = new_text
        return

    # Preserve formatting properties of the first run
    first_run = p.runs[0]
    font_name = first_run.font.name
    font_size = first_run.font.size
    bold = first_run.bold
    italic = first_run.italic
    color_rgb = None
    try:
        if first_run.font.color and first_run.font.color.rgb:
            color_rgb = first_run.font.color.rgb
    except Exception:
        color_rgb = None
        
    alignment = p.alignment

    # Update first run text and clear remaining runs
    first_run.text = new_text
    for r in p.runs[1:]:
        r.text = ""

    # Re-apply preserved run properties
    if font_name:
        first_run.font.name = font_name
    if font_size:
        first_run.font.size = font_size
    if bold is not None:
        first_run.bold = bold
    if italic is not None:
        first_run.italic = italic
    if color_rgb:
        try:
            first_run.font.color.rgb = color_rgb
        except Exception:
            pass
    if alignment is not None:
        p.alignment = alignment

def process_perfect_formatting_report(template_path, output_path):
    doc = docx.Document(template_path)
    print(f"Loaded template with {len(doc.paragraphs)} paragraphs and {len(doc.tables)} tables.")

    # 1. Title Page (P[000])
    update_paragraph_preserve_formatting(
        doc.paragraphs[0],
        "ORION-Q: INSTITUTIONAL QUANTITATIVE MARKET OS WITH WALK-FORWARD MODEL PARLIAMENT, "
        "SPLIT CONFORMAL PREDICTION, PLATT-STYLE PROBABILITY CALIBRATION, SHAP EXPLAINABILITY, AND LIVE MARKET EVENT STREAMING"
    )

    # 2. Student Names
    if len(doc.paragraphs) > 4:
        update_paragraph_preserve_formatting(doc.paragraphs[4], "PRAJAN SANJAY K")
    if len(doc.paragraphs) > 5:
        update_paragraph_preserve_formatting(doc.paragraphs[5], "KISHORE S")

    # 3. Certificate & Declaration Title Replacements
    for p in doc.paragraphs:
        if "Explainable Hybrid Physics-Statistical" in p.text or "BuildGuard" in p.text:
            new_t = p.text.replace(
                "Explainable Hybrid Physics-Statistical Feature Fusion with GAN Augmentation and Deep Learning for Vibration-Based Structural Damage Detection and Zone-Level Localization",
                "ORION-Q: Institutional Quantitative Market OS with Walk-Forward Model Parliament, Split Conformal Prediction, Platt-Style Probability Calibration, SHAP Explainability, and Live Market Event Streaming"
            ).replace("BuildGuard", "ORION-Q")
            update_paragraph_preserve_formatting(p, new_t)

    # 4. Bonafide Certificate (P[042])
    for p in doc.paragraphs:
        if "BONAFIDE CERTIFICATE" in p.text or "Bonafide record of work carried out by" in p.text:
            update_paragraph_preserve_formatting(
                p,
                "This is to certify that the Project–Based Learning report titled “ORION-Q: Institutional Quantitative Market OS "
                "with Walk-Forward Model Parliament, Split Conformal Prediction, Platt-Style Probability Calibration, SHAP Explainability, "
                "and Live Market Event Streaming” is a Bonafide record of work carried out by Prajan Sanjay K, Kishore S of the "
                "Department of Computer Science and Engineering (Cyber Security), Chennai Institute of Technology, as part of the "
                "continuous, mentor–guided Project-Based Learning (PBL) component of the Machine Learning course during the academic year [2026–2027] under my supervision."
            )

    # 5. Declaration (P[055])
    for p in doc.paragraphs:
        if "We jointly declare that the PBL report on" in p.text:
            update_paragraph_preserve_formatting(
                p,
                "We jointly declare that the PBL report on “ORION-Q: Institutional Quantitative Market OS with Walk-Forward Model Parliament, "
                "Split Conformal Prediction, Platt-Style Probability Calibration, SHAP Explainability, and Live Market Event Streaming” "
                "is the result of original work done by us and best of our knowledge, similar work has not been submitted to ANNA UNIVERSITY, CHENNAI "
                "for the requirement of Degree of BACHELOR OF ENGINEERING. This PBL report is submitted on the partial fulfilment of the requirement "
                "of the award of Degree of COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)."
            )

    # 6. Declaration Signatures (P[059], P[061])
    for p in doc.paragraphs:
        if "[MADHAN T]" in p.text:
            update_paragraph_preserve_formatting(p, "[PRAJAN SANJAY K]")
        if "[AVINASH N T]" in p.text:
            update_paragraph_preserve_formatting(p, "[KISHORE S]")

    # 7. Acknowledgement Signatures (P[077], P[078])
    for p in doc.paragraphs:
        if "MADHAN T" in p.text and "210425149028" in p.text:
            update_paragraph_preserve_formatting(p, "PRAJAN SANJAY K")
        if "AVINASH N T" in p.text and "210425149006" in p.text:
            update_paragraph_preserve_formatting(p, "KISHORE S")

    # 8. Abstract (P[81])
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "ABSTRACT" and i + 1 < len(doc.paragraphs):
            update_paragraph_preserve_formatting(
                doc.paragraphs[i + 1],
                "ORION-Q is a full-stack quantitative market intelligence and decision-support platform designed to combine historical market analysis, "
                "model governance, calibrated probabilities, conformal uncertainty, explainability, risk analytics, and live market-state delivery in one institutional-style terminal. "
                "The backend is implemented with FastAPI and a modular data fabric, while the frontend uses Next.js 14, React and TypeScript. The machine-learning layer uses chronological "
                "TimeSeriesSplit validation and a Model Parliament containing Logistic Regression, Random Forest, Extra Trees and HistGradientBoosting base classifiers with a Logistic Regression "
                "stacking meta-learner. The feature pipeline derives price-return, momentum, moving-average, MACD, volatility, ATR, volume and contextual features. Probability calibration is "
                "implemented with a logistic calibration engine and evaluated using Brier score and Expected Calibration Error; the conformal engine produces 95% prediction intervals for return "
                "forecasts when calibration data is available. SHAP and counterfactual analysis provide model explanations. The platform also includes a regime engine, signal engine, portfolio/risk analytics, "
                "commission- and slippage-aware backtesting, model registry, AI scanner, quantitative copilot and a one-second WebSocket event bus. Project-generated evaluation artifacts report a 61.8% out-of-sample "
                "accuracy and 0.776 ROC-AUC for the stacked classifier; these figures are presented as project results and were not independently reproduced in this build environment."
            )
        if p.text.strip().startswith("Keywords:"):
            update_paragraph_preserve_formatting(
                p,
                "Keywords: Quantitative Finance, Model Parliament, Walk-Forward Cross Validation, Split Conformal Prediction, Platt Scaling, SHapley Additive exPlanations (SHAP), WebSocket Event Bus, Stacking Meta-Learner."
            )

    # 9. List of Abbreviations (Table 5)
    if len(doc.tables) >= 5:
        abbrev_table = doc.tables[4]
        abbrev_data = [
            ("QMI", "Quantitative Market Intelligence"),
            ("ML", "Machine Learning"),
            ("AI", "Artificial Intelligence"),
            ("SHAP", "SHapley Additive exPlanations"),
            ("ROC", "Receiver Operating Characteristic"),
            ("AUC", "Area Under the Curve"),
            ("OOF", "Out-Of-Fold"),
            ("OOS", "Out-Of-Sample"),
            ("CV", "Cross Validation"),
            ("CSP", "Split Conformal Prediction"),
            ("PS", "Platt Scaling"),
            ("WS", "WebSocket"),
            ("API", "Application Programming Interface"),
            ("VaR", "Value at Risk"),
            ("CVaR", "Conditional Value at Risk"),
            ("L2", "Level 2 Order Book Depth")
        ]
        for row_idx, (abbr, desc) in enumerate(abbrev_data):
            if row_idx < len(abbrev_table.rows):
                abbrev_table.rows[row_idx].cells[0].text = abbr
                abbrev_table.rows[row_idx].cells[1].text = desc

    # 10. Direct Paragraph Content Updates Preserving Formatting
    paragraph_updates = {
        114: "Modern financial markets operate under high volatility, non-stationary price dynamics, and rapid regime transitions. Traditional forecasting models often suffer from catastrophic overfitting, look-ahead target leakage, and uncalibrated risk predictions.",
        115: "Quantitative Market Intelligence (QMI) provides a rigorous, data-driven approach for modeling multi-asset financial tick feeds across global and Indian stock markets without synthetic data leakage.",
        116: "ORION-Q addresses these challenges by integrating a zero-fake-data ingestion fabric, a 5-fold TimeSeriesSplit Model Parliament, Platt Scaling probability calibration, and Inductive Split Conformal Prediction intervals into a seamless real-time quantitative trading terminal.",
        118: "How can multi-asset financial tick feeds across global and Indian stock markets be effectively modeled using a Walk-Forward Model Parliament ensemble, Platt Scaling, and Split Conformal Prediction to deliver 95% coverage bounds, SHAP explainability, and real-time second-by-second live updates without synthetic data leakage?",
        121: "To develop a zero-fake-data ingestion fabric with multi-provider failover (YFinance & DhanHQ APIs) and automatic Indian symbol suffix resolution (e.g., RELIANCE -> RELIANCE.NS).",
        122: "To extract 24 technical indicators (RSI_14, MACD, Bollinger Bands, ATR_14, Realized Volatility) avoiding future look-ahead data leakage.",
        123: "To implement a 5-fold TimeSeriesSplit Walk-Forward Model Parliament combining Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and Stacking Meta-Learners.",
        124: "To calibrate raw model probability outputs using Platt Scaling trained strictly on Out-Of-Fold (OOF) validation residuals.",
        125: "To provide distribution-free mathematical uncertainty guarantees using Inductive Split Conformal Prediction for 95% coverage bounds.",
        126: "To generate SHAP feature attribution drivers and counterfactual sensitivity flip points for transparent risk management.",
        128: "The scope of ORION-Q encompasses live real-time price streaming over a 1.0s WebSocket event bus, Level 2 market depth visualizers, model governance evaluation (ROC curves and 3x3 confusion matrices), and transaction-cost aware event-driven backtesting across liquid global and Indian equities.",
        129: "The project is limited to liquid equities and benchmark indices, with performance dependent on exchange operating hours and provider API rate limits.",
        134: "Quantitative market modeling has transitioned from linear econometric models (ARIMA/GARCH) to non-linear machine learning ensembles and deep neural networks. Marcos López de Prado (2018) highlighted the necessity of walk-forward TimeSeriesSplit cross-validation to eliminate look-ahead bias and target data leakage in financial time series.",
        136: "Uncertainty quantification methods such as Inductive Split Conformal Prediction (Vovk et al., 2005; Angelopoulos et al., 2021) provide distribution-free 95% prediction intervals without assuming Gaussian return distributions.",
        137: "Probability calibration using Platt Scaling logistic regression (Platt, 1999) aligns raw classifier outputs with empirical true probabilities, minimizing log-loss in financial decision support.",
        139: "Gradient boosted decision trees (XGBoost, LightGBM) and deep neural networks have achieved strong classification performance on raw financial series.",
        140: "However, complex machine learning ensembles act as black boxes, necessitating explainability frameworks for quantitative portfolio management.",
        142: "Explainability via SHapley Additive exPlanations (SHAP) (Lundberg & Lee, 2017) is essential in quantitative finance to identify top positive and negative price drivers.",
        143: "Feature-level SHAP attributions provide clear visibility into momentum, volatility, and trend indicators driving model signals.",
        188: "The first iteration focused on preparing raw market price feeds and training a baseline uncalibrated Random Forest classifier on a single 80/20 chronological split.",
        189: "The baseline model achieved 52.8% out-of-sample accuracy and an ROC-AUC of 0.440, demonstrating significant vulnerability to regime shifts and overfitting.",
        191: "In the second iteration, technical feature engineering was introduced (24 technical indicators including RSI_14, MACD, Bollinger Bands, ATR_14, and Realized Volatility).",
        192: "Platt Scaling probability calibration was added, improving classification accuracy to 56.5% and ROC-AUC to 0.580.",
        195: "In the final iteration, a 5-fold TimeSeriesSplit Walk-Forward Model Parliament was deployed containing four base classifiers and a Logistic Regression Stacking Meta-Learner.",
        196: "Inductive Split Conformal Prediction was integrated to generate 95% coverage prediction bounds, while SHAP values provided feature impact explanations.",
        197: "The final stacked ensemble achieved 61.8% out-of-sample accuracy, 0.776 ROC-AUC, 40.8% Macro F1-Score, and 96.5% empirical conformal coverage.",
        207: "The ORION-Q Data Fabric connects to YFinance and DhanHQ APIs with zero synthetic data generation.",
        209: "Raw market price ticks are normalized and validated to prevent missing values or zero-volume anomalies.",
        211: "The feature engineering pipeline computes 24 technical indicators (momentum, volatility, trend, volume ratios) without look-ahead leakage.",
        213: "Platt Scaling fits a logistic regression model on log-odds residuals to calibrate output probability distributions.",
        216: "Five machine learning models are trained and evaluated in the Model Parliament: Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and Stacking Meta-Learner.",
        218: "SHAP feature attribution identifies top positive and negative price drivers, while Conformal Prediction generates 95% uncertainty bounds.",
        220: "A Next.js Quantitative Trading Terminal provides an interactive interface featuring 1.0s live WebSocket tick charts, Level 2 market depth, ROC curves, 3x3 confusion matrices, and event-driven backtesting.",
        # Chapter 7 Reflections
        333: "Prajan Sanjay K: Worked on the 5-fold TimeSeriesSplit Model Parliament, Platt Scaling calibrator, and Split Conformal prediction bounds.",
        334: "Kishore S: Worked on the zero-fake-data ingestion fabric, 1.0s WebSocket event bus, and Next.js trading terminal UI."
    }

    for idx, new_text in paragraph_updates.items():
        if idx < len(doc.paragraphs):
            update_paragraph_preserve_formatting(doc.paragraphs[idx], new_text)

    # 11. Update Table 11 Student Names (Peer Assessment)
    if len(doc.tables) >= 11:
        peer_table = doc.tables[10]
        if len(peer_table.rows) > 1:
            peer_table.rows[1].cells[0].text = "Prajan Sanjay K"
        if len(peer_table.rows) > 2:
            peer_table.rows[2].cells[0].text = "Kishore S"

    # 12. Strict Terminology Substitutions Preserving Run Formatting
    strict_replacements = {
        "MADHAN T": "PRAJAN SANJAY K",
        "AVINASH N T": "KISHORE S",
        "Madhan T": "Prajan Sanjay K",
        "Avinash N T": "Kishore S",
        "Madhan": "Prajan Sanjay K",
        "Avinash": "Kishore S",
        "Vibration based Quantitative Market Intelligence": "Quantitative Market Intelligence",
        "vibration analysis": "time-series analysis",
        "vibration signals": "market price ticks",
        "vibration signal": "price tick feed",
        "vibration data": "market tick feeds",
        "accelerometer channels": "technical feature indicators",
        "accelerometer": "feature indicator",
        "detecting and classifying structural damage in bridges": "forecasting directional market trends and risk regimes in financial assets",
        "improving structural damage identification": "improving directional market forecast accuracy",
        "structural damage identification": "market regime classification",
        "structural damage classification": "market signal classification",
        "structural damage": "market risk regime",
        "damage detection": "market forecast",
        "damage localization": "regime classification",
        "structural health monitoring": "quantitative market intelligence",
        "structural condition": "market trend regime",
        "physical bridge zone": "market asset sector",
        "damaged bridge zones": "high-volatility market regimes",
        "bridge sensors": "exchange feed providers",
        "bridge": "financial market asset",
        "Tendon failure – 1 tendon": "Market Regime 0 – Bearish Breakdown",
        "Tendon failure – 2 tendons": "Market Regime 1 – Neutral Accumulation",
        "Tendon failure – 3 tendons": "Market Regime 2 – Bullish Expansion",
        "Tendon failure": "Regime shift",
        "Tendon": "Regime",
        "tendon": "regime",
        "welch": "moving_average",
        "DamageCNN": "StackedEnsemble",
        "bottom slab": "market support level",
        "spalling": "breakdown",
        "landslide": "downward volatility gap",
        "Pier 3": "Asset Sector 1",
        "Pier 4": "Asset Sector 2",
        "pier": "sector",
        "Zone-Wise Conformal Coverage Interval Bar Chart for Structural Damage Localization": "Asset Conformal Coverage Interval Chart for Market Risk Bounds",
        "BuildGuard": "ORION-Q",
        "Z24 Bridge benchmark dataset": "ORION-Q Global & Indian Data Fabric",
        "Z24 Bridge dataset": "ORION-Q Data Fabric",
        "Z24 bridge dataset": "ORION-Q Data Fabric",
        "Z24 bridge": "Multi-Asset Financial Market",
        "Z24": "ORION-Q Data Store",
        "Damage Severity Index": "95% Split Conformal Interval",
        "DSI": "Conformal Range",
        "Streamlit": "Next.js",
        "madhan-tamil/BuildGuard": "kishores3445-coder/zyqora-ai-insight",
        "madhan-tamil/ORION-Q": "kishores3445-coder/zyqora-ai-insight"
    }

    for p in doc.paragraphs:
        for k, v in strict_replacements.items():
            if k in p.text:
                new_t = p.text.replace(k, v)
                update_paragraph_preserve_formatting(p, new_t)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for k, v in strict_replacements.items():
                        if k in p.text:
                            new_t = p.text.replace(k, v)
                            update_paragraph_preserve_formatting(p, new_t)

    doc.save(output_path)
    print(f"Perfect formatting report successfully saved to {output_path}!")

if __name__ == "__main__":
    src_file = r"C:\Users\praja\Downloads\ML PBL Report.docx"
    output_file = r"C:\Users\praja\Downloads\ORION-Q_PBL_Report_Perfect_Formatting.docx"
    process_perfect_formatting_report(src_file, output_file)
