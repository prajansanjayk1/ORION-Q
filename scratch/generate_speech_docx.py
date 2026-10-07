import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = docx.Document()

# Page Setup
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

def style_run(run, font_name='Times New Roman', font_size=12, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

# Title
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title_p.add_run('ORION-Q: INSTITUTIONAL QUANTITATIVE MARKET OS\nPRESENTATION SPEECH SCRIPT')
style_run(r, font_name='Times New Roman', font_size=16, bold=True, color_rgb=(15, 23, 42))

sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sub_p.add_run('CZ5305 – Machine Learning PBL | Final Project Review\nDepartment of CSE (Cyber Security) | Chennai Institute of Technology')
style_run(r2, font_name='Times New Roman', font_size=11, italic=True, color_rgb=(71, 85, 105))

doc.add_paragraph()

# Team Info Table
table = doc.add_table(rows=4, cols=2)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = [
    ('Project Title', 'ORION-Q: Institutional Quantitative Market OS'),
    ('Team Authors', 'Prajan Sanjay K (210425149037) & Kishore S (210425149025)'),
    ('Faculty Mentor', 'Dr. Sundarambal M.E., Ph.D. (Professor, CSE Cyber Security)'),
    ('GitHub Repository', 'https://github.com/prajansanjayk1/ORION-Q')
]

for idx, (label, val) in enumerate(headers):
    row = table.rows[idx]
    r0 = row.cells[0].paragraphs[0].add_run(label)
    style_run(r0, font_name='Times New Roman', font_size=11, bold=True, color_rgb=(15, 23, 42))
    r1 = row.cells[1].paragraphs[0].add_run(val)
    style_run(r1, font_name='Times New Roman', font_size=11, color_rgb=(30, 41, 59))

doc.add_paragraph()

# Slides
slides = [
    {
        'num': '1',
        'title': 'Slide 1: Title & Team Introduction',
        'speaker': 'Prajan Sanjay K',
        'time': '0:00 - 0:45',
        'speech': 'Good morning respected mentor Dr. Sundarambal ma\'am and internal evaluators. I am Prajan Sanjay K alongside my project partner Kishore S from the Department of Computer Science and Engineering (Cyber Security), Chennai Institute of Technology.\n\nToday, we are presenting our Machine Learning Project-Based Learning review titled ORION-Q: Institutional Quantitative Market OS with Walk-Forward Model Parliament, Split Conformal Prediction, SHAP Explainability and Live Market Event Streaming.'
    },
    {
        'num': '2',
        'title': 'Slide 2: Problem Statement & Objectives',
        'speaker': 'Prajan Sanjay K',
        'time': '0:45 - 1:45',
        'speech': 'To begin with the problem statement: Financial markets are notoriously non-stationary, highly volatile, and suffer from rapid regime shifts. Traditional machine learning models in finance fail because they overfit noise, introduce look-ahead bias (future data leakage), and produce uncalibrated, unexplainable probabilities.\n\nTraders, quantitative analysts, and risk managers face a major gap: they lack an integrated, leakage-free platform that provides uncertainty-aware predictions alongside clear feature explanations.\n\nTo solve this, our objectives in ORION-Q were:\n1. Build a zero-fake-data ingestion fabric utilizing real market data from Yahoo Finance and DhanHQ.\n2. Construct a 24-indicator leakage-free technical feature pipeline.\n3. Implement a 5-fold TimeSeriesSplit walk-forward Model Parliament featuring a Stacking Meta-Learner.\n4. Apply Platt Scaling for probability calibration and Split Conformal Prediction for 95% non-parametric confidence bounds.\n5. Integrate SHAP feature drivers, backtesting, and a live 1-second WebSocket terminal.'
    },
    {
        'num': '3',
        'title': 'Slide 3: Input, Analysis & Insights',
        'speaker': 'Prajan Sanjay K',
        'time': '1:45 - 2:45',
        'speech': 'Moving to our data input and analysis: We ingest real-time and historical OHLCV data across liquid global and Indian equities such as Apple, Microsoft, Reliance, and TCS—purging all synthetic data.\n\nFrom raw ticks, we extract 24 technical indicators using past information exclusively to avoid look-ahead bias.\n\nKey Insights from our training:\n- Top Feature Drivers: TreeSHAP analysis shows short-term price momentum (close_return_1 at 0.162) and trend/volume indicators (rsi_14 at 0.121 and macd_hist at 0.083) dominate signal generation.\n- Ensemble Power: Our Stacking Meta-Learner achieved 61.8% Out-of-Sample Accuracy compared to 54.3% for the best individual model (Extra Trees).\n- Iterative Improvement: Over pipeline iterations, accuracy improved from 52.8% to 61.8%, and ROC-AUC jumped from 0.440 to 0.776.'
    },
    {
        'num': '4',
        'title': 'Slide 4: Technical Approach & Architecture',
        'speaker': 'Prajan Sanjay K',
        'time': '2:45 - 3:45',
        'speech': 'Here is our end-to-end ORION-Q Architecture: Our stack is powered by Python 3.10+, FastAPI, scikit-learn, and a Next.js 14 Zerodha-inspired Quantitative Terminal.\n\nData flows from Yahoo Finance and DhanHQ into our validation engine. Once 24 technical features are extracted, they pass into our Model Parliament consisting of Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and a Stacking Meta-Learner.\n\nThe outputs are calibrated using Platt Scaling, passed through Split Conformal Prediction for 95% coverage bounds, and explained using SHAP values. Finally, signals are broadcast over a 1-second WebSocket event bus directly into our live Next.js Terminal UI.\n\nNow, I will hand over the presentation to Kishore to discuss our Feasibility, Experimental Results, and Conclusion.'
    },
    {
        'num': '5',
        'title': 'Slide 5: Feasibility, Risk & Challenges',
        'speaker': 'Kishore S',
        'time': '3:45 - 4:45',
        'speech': 'Thank you, Prajan.\n\nSpeaking on Feasibility: Our modular architecture allowed us to test data ingestion, feature engineering, model training, and UI components independently. Using efficient classical models and scikit-learn ensembles eliminated the need for costly GPUs, allowing us to complete the working terminal within our 12-week PBL schedule.\n\nRegarding Risks and Challenges: Financial data presents high risks of overfitting and target leakage. Uncalibrated black-box predictions are dangerous for financial risk management.\n\nOur Mitigations:\n- We strictly enforced chronological TimeSeriesSplit to eliminate future data leakage.\n- We applied out-of-fold Platt scaling and Split Conformal Prediction, achieving 96.5% empirical coverage, giving traders true non-parametric uncertainty bounds.\n- Multi-provider failover and SHAP feature attribution ensure data continuity and model auditability.'
    },
    {
        'num': '6',
        'title': 'Slide 6: Results & Applications',
        'speaker': 'Kishore S',
        'time': '4:45 - 5:45',
        'speech': 'Looking at our Experimental Results:\n- As shown in our Model Parliament comparison bar chart, the Stacked Ensemble proved to be our champion model, achieving 61.8% OOS Accuracy and an ROC-AUC of 0.776.\n- Our Out-Of-Fold 3-class confusion matrix highlights strong Bullish recall (54 out of 60 correct), though class imbalance affected Neutral regime recovery.\n- In our decision support UI output, each prediction displays the signal (BUY/SELL/HOLD), calibrated probability (e.g., 97.6%), and 95% conformal uncertainty bounds (e.g., +1.1% to +3.8%).\n\nReal-World Applications:\n1. Institutional quantitative decision support for buy-side traders.\n2. Real-time portfolio risk analytics (Value at Risk & Conditional VaR).\n3. Model governance and auditability using SHAP feature attribution.\n4. Transaction-cost-aware strategy backtesting.'
    },
    {
        'num': '7',
        'title': 'Slide 7: Conclusion, Limitations & Future Scope',
        'speaker': 'Kishore S',
        'time': '5:45 - 6:30',
        'speech': 'To conclude: We successfully engineered ORION-Q, an institutional quantitative market OS that combines walk-forward Model Parliaments, Platt scaling, split conformal prediction, and live WebSocket streaming.\n\nLimitations:\n- Evaluation was conducted on a 110-sample out-of-fold validation set.\n- Class imbalance caused the model to favor directional regimes over Neutral states.\n- The current version operates as a decision support OS without automated order execution adapters.\n\nFuture Scope:\n1. Expanding datasets across multi-year asset histories and paper-trading environments.\n2. Applying class-rebalancing techniques to improve Neutral regime classification.\n3. Incorporating Level-2 order-book depth and news sentiment analysis.'
    },
    {
        'num': '8',
        'title': 'Slide 8: Thank You & GitHub Link',
        'speaker': 'Kishore S (Jointly with Prajan)',
        'time': '6:30 - 7:00',
        'speech': 'Our entire codebase, FastAPI services, Next.js terminal, model registry, and documentation are open-sourced on GitHub at https://github.com/prajansanjayk1/ORION-Q.\n\nThank you Dr. Sundarambal ma\'am and external evaluators. We are now open for questions!'
    }
]

for s in slides:
    hp = doc.add_paragraph()
    r = hp.add_run(s['title'])
    style_run(r, font_name='Times New Roman', font_size=13, bold=True, color_rgb=(15, 23, 42))
    
    meta_p = doc.add_paragraph()
    r_sp = meta_p.add_run(f"Primary Speaker: {s['speaker']}   |   Allocated Time: {s['time']}")
    style_run(r_sp, font_name='Times New Roman', font_size=10, bold=True, italic=True, color_rgb=(2, 132, 199))
    
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.line_spacing = 1.15
    sp_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_speech = sp_p.add_run(s['speech'])
    style_run(r_speech, font_name='Times New Roman', font_size=11, color_rgb=(30, 41, 59))
    
    doc.add_paragraph()

doc.save('C:\\Users\\praja\\Downloads\\ORION-Q_Presentation_Speech_Prajan_Kishore.docx')
print('GENERATED DOCX SUCCESSFULLY')
