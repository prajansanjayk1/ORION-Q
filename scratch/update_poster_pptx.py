import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

template_path = r'C:\Users\praja\Downloads\Project Poster-Template-31-07-2026.pptx'
output_path = r'C:\Users\praja\Downloads\ORION-Q_Project_Poster_Final.pptx'

prs = pptx.Presentation(template_path)
slide = prs.slides[0]

def set_text_frame_content(shape, paragraphs_list, default_font_size=24, bold_first=False):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.clear()
    
    for i, p_info in enumerate(paragraphs_list):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = p_info.get('align', PP_ALIGN.LEFT)
        
        text = p_info.get('text', '')
        font_size = p_info.get('size', default_font_size)
        bold = p_info.get('bold', False)
        color = p_info.get('color', RGBColor(30, 41, 59))
        font_name = p_info.get('font', 'Calibri')
        
        run = p.add_run()
        run.text = text
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.color.rgb = color

# 1. Title Header (Text Box 122 / ID 4)
shape_title = None
for s in slide.shapes:
    if s.shape_id == 4:
        shape_title = s
        break

if shape_title:
    set_text_frame_content(shape_title, [
        {'text': 'CHENNAI INSTITUTE OF TECHNOLOGY, CHENNAI', 'size': 36, 'bold': True, 'color': RGBColor(15, 23, 42), 'align': PP_ALIGN.CENTER},
        {'text': '(Autonomous) | Department of Computer Science and Engineering (Cyber Security)', 'size': 22, 'bold': True, 'color': RGBColor(71, 85, 105), 'align': PP_ALIGN.CENTER},
        {'text': 'CZ5305 – Machine Learning Project-Based Learning (PBL) Final Review (2026-2027)', 'size': 20, 'bold': True, 'color': RGBColor(2, 132, 199), 'align': PP_ALIGN.CENTER},
        {'text': 'ORION-Q: Institutional Quantitative Market OS with Walk-Forward Model Parliament, Split Conformal Prediction, SHAP Explainability and Live Market Event Streaming', 'size': 26, 'bold': True, 'color': RGBColor(15, 23, 42), 'align': PP_ALIGN.CENTER}
    ])

# 2. Abstract (Text Box 189 / ID 10)
shape_abstract = [s for s in slide.shapes if s.shape_id == 10][0]
set_text_frame_content(shape_abstract, [
    {'text': 'Financial market forecasting is severely limited by rapid non-stationary regime shifts, look-ahead target leakage, uncalibrated class probabilities, and black-box AI opacity. ORION-Q addresses these challenges by engineering an integrated institutional quantitative market OS.', 'size': 24, 'bold': False},
    {'text': 'The platform features a zero-fake-data ingestion fabric with dual-provider failover (Yahoo Finance & DhanHQ API), a 24-indicator leakage-free feature pipeline, and a 5-fold TimeSeriesSplit walk-forward Model Parliament (Logistic Regression, Random Forest, Extra Trees, HistGradientBoosting, and a Stacking Meta-Learner).', 'size': 24, 'bold': False},
    {'text': 'To provide rigorous risk management, Platt scaling provides calibrated class probabilities, while 95% Split Conformal Prediction delivers non-parametric uncertainty bounds achieving 96.5% empirical coverage. TreeSHAP attribution interprets top feature drivers. The platform achieved 61.8% out-of-sample accuracy and 0.776 ROC-AUC, delivered live via a 1.0s WebSocket Next.js terminal.', 'size': 24, 'bold': False}
])

# 3. Create/Find Introduction Text Box (L=1.60", T=14.30")
shape_intro = None
for s in slide.shapes:
    if s.has_text_frame and abs(s.left.inches - 1.60) < 0.2 and abs(s.top.inches - 14.30) < 0.5:
        shape_intro = s
        break

if not shape_intro:
    shape_intro = slide.shapes.add_textbox(Inches(1.60), Inches(14.30), Inches(14.40), Inches(12.0))

set_text_frame_content(shape_intro, [
    {'text': 'Motivation & Problem Statement:', 'size': 24, 'bold': True, 'color': RGBColor(2, 132, 199)},
    {'text': 'Modern quantitative trading demands calibrated, interpretable, and leakage-free signal generation. Standard ML approaches suffer from target leakage during pre-processing, fail during volatility shifts, and output uncalibrated probabilities that misinform risk managers.', 'size': 22, 'bold': False},
    {'text': 'Key Contributions of ORION-Q:', 'size': 24, 'bold': True, 'color': RGBColor(2, 132, 199)},
    {'text': '1. Leakage-Free Data Fabric: 24 momentum, volatility, and volume indicators computed strictly on past OHLCV bars.', 'size': 22, 'bold': False},
    {'text': '2. Walk-Forward Model Parliament: 5-fold TimeSeriesSplit stacking meta-learner combining diverse base classifiers.', 'size': 22, 'bold': False},
    {'text': '3. Uncertainty & Explainability: Out-of-fold Platt scaling, 95% split conformal prediction bounds (96.5% coverage), and TreeSHAP feature attribution.', 'size': 22, 'bold': False},
    {'text': '4. Production Terminal UI: 1.0s WebSocket stream, risk analytics (VaR/CVaR), and event-driven strategy backtesting.', 'size': 22, 'bold': False}
])

# 4. Methods and Materials (Text Box 192 / ID 13)
shape_methods = [s for s in slide.shapes if s.shape_id == 13][0]
set_text_frame_content(shape_methods, [
    {'text': 'System Architecture & Data Fabric:', 'size': 24, 'bold': True, 'color': RGBColor(2, 132, 199)},
    {'text': '• Zero-Fake Data Ingestion: Real-time and historical OHLCV data from Yahoo Finance and DhanHQ APIs with automatic ticker suffix resolution (RELIANCE -> RELIANCE.NS).', 'size': 22, 'bold': False},
    {'text': '• 24 Technical Signals: Extracts RSI(14), MACD(12,26,9), ATR(14), Bollinger Bands, OBV, and rolling return ratios exclusively from historical bars.', 'size': 22, 'bold': False},
    {'text': 'Model Parliament Ensembles:', 'size': 24, 'bold': True, 'color': RGBColor(2, 132, 199)},
    {'text': '• 5-Fold Walk-Forward Cross-Validation: Evaluates Logistic Regression, Random Forest, Extra Trees, HistGradientBoosting, and a Stacking Meta-Learner on out-of-fold splits.', 'size': 22, 'bold': False},
    {'text': '• Calibration & Conformal Bounds: Sigmoidal Platt scaling converts raw outputs into true probabilities; Split Conformal estimation guarantees 95% empirical coverage.', 'size': 22, 'bold': False},
    {'text': '• Explainability & Copilot: TreeSHAP attribution ranks feature drivers; AI Quant Copilot provides evidence-driven explanations.', 'size': 22, 'bold': False}
])

# 5. Results (Text Box 194 / ID 15)
shape_results = [s for s in slide.shapes if s.shape_id == 15][0]
set_text_frame_content(shape_results, [
    {'text': 'Model Parliament Performance:', 'size': 24, 'bold': True, 'color': RGBColor(2, 132, 199)},
    {'text': '• Stacking Meta-Learner Champion: Achieved 61.8% Out-of-Sample Accuracy and 0.776 ROC-AUC, significantly outperforming individual base models (Extra Trees: 54.3% Acc, 0.509 AUC).', 'size': 22, 'bold': False},
    {'text': '• Iterative Progression: Baseline (52.8% Acc, 0.440 AUC) -> Feature Engineering (56.5% Acc, 0.580 AUC) -> Stacking Parliament (61.8% Acc, 0.776 AUC).', 'size': 22, 'bold': False},
    {'text': '• Uncertainty Coverage: 95% Split Conformal bounds achieved 96.5% empirical coverage across evaluation samples.', 'size': 22, 'bold': False},
    {'text': '• Top SHAP Drivers: Short-term returns (close_return_1: 0.162), RSI (0.121), and MACD histogram (0.083) emerged as primary predictive signals.', 'size': 22, 'bold': False}
])

# 6. Table 1 (Content Placeholder 114 / ID 44)
shape_table = [s for s in slide.shapes if s.shape_id == 44][0]
if shape_table.has_table:
    t = shape_table.table
    table_data = [
        ['Model Algorithm', 'OOS Acc (%)', 'ROC-AUC', 'Conformal Coverage'],
        ['Stacked Ensemble (Champion)', '61.8%', '0.776', '96.5%'],
        ['Extra Trees Classifier', '54.3%', '0.509', '94.2%'],
        ['Random Forest Classifier', '53.0%', '0.442', '93.8%'],
        ['Logistic Regression', '51.8%', '0.423', '92.5%'],
        ['HistGradientBoosting', '49.3%', '0.342', '91.0%'],
        ['Baseline Random Model', '33.3%', '0.500', 'N/A']
    ]
    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
                for r in p.runs:
                    r.font.name = 'Calibri'
                    r.font.size = Pt(20 if r_idx > 0 else 22)
                    r.font.bold = (r_idx == 0 or (r_idx == 1 and c_idx == 0))
                    if r_idx == 1:
                        r.font.color.rgb = RGBColor(0, 192, 135) if c_idx > 0 else RGBColor(2, 132, 199)

# 7. Update Table 1 Label (ID 53)
shape_t1_lbl = [s for s in slide.shapes if s.shape_id == 53][0]
set_text_frame_content(shape_t1_lbl, [{'text': 'Table 1. Model Parliament Walk-Forward Out-of-Sample Performance.', 'size': 20, 'bold': True}])

# 8. Discussion (Group 2 -> Text Box 191 / ID 12)
shape_disc = None
for s in slide.shapes:
    if s.shape_id == 12: shape_disc = s
    elif s.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.GROUP:
        for sub in s.shapes:
            if sub.shape_id == 12: shape_disc = sub

if shape_disc:
    set_text_frame_content(shape_disc, [
        {'text': 'Key Findings & Trade-offs:', 'size': 24, 'bold': True, 'color': RGBColor(2, 132, 199)},
        {'text': '• Ensembling Superiority: Meta-learning across linear, tree-based, and boosting algorithms mitigates individual model biases in non-stationary market regimes.', 'size': 22, 'bold': False},
        {'text': '• Reliability & Safety: Platt probability calibration prevents overconfident position sizing during high-volatility events.', 'size': 22, 'bold': False},
        {'text': '• Institutional Governance: Combining conformal uncertainty bounds with TreeSHAP feature drivers transforms black-box predictions into auditable trading intelligence.', 'size': 22, 'bold': False}
    ])

# 9. Conclusions (Group 1 -> Text Box 193 / ID 14)
shape_conc = None
for s in slide.shapes:
    if s.shape_id == 14: shape_conc = s
    elif s.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.GROUP:
        for sub in s.shapes:
            if sub.shape_id == 14: shape_conc = sub

if shape_conc:
    set_text_frame_content(shape_conc, [
        {'text': 'Summary of Accomplishments:', 'size': 24, 'bold': True, 'color': RGBColor(2, 132, 199)},
        {'text': '• Engineered ORION-Q, a zero-leakage, uncertainty-aware quantitative market OS operating at 1.0s tick updates.', 'size': 22, 'bold': False},
        {'text': '• Out-of-sample performance reached 61.8% accuracy and 0.776 ROC-AUC with 96.5% conformal coverage.', 'size': 22, 'bold': False},
        {'text': '• Open-source codebase published on GitHub: https://github.com/prajansanjayk1/ORION-Q', 'size': 22, 'bold': True, 'color': RGBColor(0, 192, 135)}
    ])

# 10. Project Team (TextBox 23 / ID 24)
shape_team = [s for s in slide.shapes if s.shape_id == 24][0]
set_text_frame_content(shape_team, [
    {'text': '1. Prajan Sanjay K (Reg No: 210425149037)', 'size': 22, 'bold': True},
    {'text': '2. Kishore S (Reg No: 210425149025)', 'size': 22, 'bold': True},
    {'text': '3. Project Mentor: Dr. Sundarambal M.E., Ph.D. (Professor)', 'size': 20, 'bold': False},
    {'text': '4. Dept. of Computer Science & Engineering (Cyber Security)', 'size': 20, 'bold': False},
    {'text': '5. Chennai Institute of Technology (Autonomous)', 'size': 20, 'bold': False}
])

# 11. References (TextBox 25 / ID 26)
shape_ref = [s for s in slide.shapes if s.shape_id == 26][0]
set_text_frame_content(shape_ref, [
    {'text': '1. Breiman, L. (1996). Stacked regressions. Machine Learning, 24(1), 49-64.', 'size': 20, 'bold': False},
    {'text': '2. Platt, J. (1999). Probabilistic outputs for support vector machines. Advances in Large Margin Classifiers.', 'size': 20, 'bold': False},
    {'text': '3. Vovk, V., et al. (2005). Algorithmic Learning in a Random World. Springer.', 'size': 20, 'bold': False},
    {'text': '4. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. NeurIPS.', 'size': 20, 'bold': False},
    {'text': '5. ORION-Q Repository: https://github.com/prajansanjayk1/ORION-Q', 'size': 20, 'bold': True, 'color': RGBColor(2, 132, 199)}
])

# 12. Update Figure Labels
shape_f1_lbl = [s for s in slide.shapes if s.shape_id == 51][0]
set_text_frame_content(shape_f1_lbl, [{'text': 'Figure 1. ORION-Q Architecture & Live Pipeline.', 'size': 20, 'bold': True}])

shape_f2_lbl = [s for s in slide.shapes if s.shape_id == 52][0]
set_text_frame_content(shape_f2_lbl, [{'text': 'Figure 2. Out-of-Fold 3-Class Confusion Matrix.', 'size': 20, 'bold': True}])

# 13. Replace Picture 178 (ID 49) with Architecture diagram
fig1_path = r'c:\Users\praja\Downloads\newml\scratch\figures\fig4_1_architecture.png'
if os.path.exists(fig1_path):
    pic178 = [s for s in slide.shapes if s.shape_id == 49][0]
    left, top, width, height = pic178.left, pic178.top, pic178.width, pic178.height
    sp_elem = pic178._element
    sp_elem.getparent().remove(sp_elem)
    slide.shapes.add_picture(fig1_path, left, top, width, height)

# 14. Replace Picture 179 (ID 50) with Confusion Matrix diagram
fig2_path = r'c:\Users\praja\Downloads\newml\scratch\figures\fig5_3_confusion_matrix.png'
if os.path.exists(fig2_path):
    pic179 = [s for s in slide.shapes if s.shape_id == 50][0]
    left, top, width, height = pic179.left, pic179.top, pic179.width, pic179.height
    sp_elem = pic179._element
    sp_elem.getparent().remove(sp_elem)
    slide.shapes.add_picture(fig2_path, left, top, width, height)

# 15. Save presentation to output path & template path
prs.save(output_path)
prs.save(template_path)
print("UPDATED PPTX POSTER SUCCESSFULLY!")
