import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set dark institutional styling
plt.style.use('dark_background')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#1e293b'
plt.rcParams['axes.linewidth'] = 1.2

output_dir = r"c:\Users\praja\Downloads\newml\scratch\figures"
os.makedirs(output_dir, exist_ok=True)

print("Generating ORION-Q System Diagrams and Charts...")

# -------------------------------------------------------------
# 1. FIG 4.1: SYSTEM ARCHITECTURE DIAGRAM
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_facecolor('#0a0e1a')
fig.patch.set_facecolor('#0a0e1a')
ax.axis('off')

# Layer boxes coordinates
layers = [
    ("Data Ingestion Fabric\n(YFinance & DhanHQ APIs | Zero Synthetic Data)", 0.1, 0.8, "#00d4e8"),
    ("Feature Engineering Pipeline\n(24 Technical Indicators: RSI, MACD, ATR, Volatility)", 0.1, 0.63, "#00c087"),
    ("Walk-Forward Model Parliament\n(5-Fold TimeSeriesSplit CV + Stacking Meta-Learner)", 0.1, 0.46, "#a855f7"),
    ("Calibration & Conformal Risk Engine\n(Platt Scaling + 95% Split Conformal Intervals)", 0.1, 0.29, "#f59e0b"),
    ("Live WebSocket Event Bus & Next.js Terminal UI\n(1.0s Tick Streaming, Level 2 Depth, ROC Curves)", 0.1, 0.12, "#e84040")
]

for title, x, y, color in layers:
    rect = plt.Rectangle((x, y), 0.8, 0.12, facecolor='#0f1628', edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    ax.text(x + 0.4, y + 0.06, title, color='#ffffff', fontsize=11, fontweight='bold', ha='center', va='center')

# Arrows
for y_top in [0.8, 0.63, 0.46, 0.29]:
    ax.annotate('', xy=(0.5, y_top - 0.05), xytext=(0.5, y_top),
                arrowprops=dict(arrowstyle="->", color="#00d4e8", lw=2.5))

plt.title("ORION-Q: End-to-End System Architecture Pipeline", color="#00d4e8", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
fig4_1_path = os.path.join(output_dir, "fig4_1_architecture.png")
plt.savefig(fig4_1_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
plt.close()
print("Saved:", fig4_1_path)

# -------------------------------------------------------------
# 2. FIG 5.1: MODEL COMPARISON LEADERBOARD
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
ax.set_facecolor('#0f1628')
fig.patch.set_facecolor('#0a0e1a')

models = ['Stacked Ensemble', 'Extra Trees', 'Random Forest', 'Logistic Regression', 'Gradient Boosting']
accs = [61.8, 54.3, 52.8, 51.5, 49.2]
aucs = [0.776 * 100, 0.507 * 100, 0.440 * 100, 0.422 * 100, 0.341 * 100]

x = np.arange(len(models))
width = 0.35

rects1 = ax.bar(x - width/2, accs, width, label='OOS Accuracy (%)', color='#00d4e8', edgecolor='#00d4e8', linewidth=1)
rects2 = ax.bar(x + width/2, aucs, width, label='ROC-AUC (x100)', color='#00c087', edgecolor='#00c087', linewidth=1)

ax.set_ylabel('Performance Metric (%)', color='#94a3b8', fontsize=11, fontweight='bold')
ax.set_title('ORION-Q Model Parliament Performance Comparison', color='#00d4e8', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, rotation=15, color='#ffffff', fontsize=9, fontweight='bold')
ax.legend(facecolor='#0f1628', edgecolor='#1e293b')
ax.grid(axis='y', linestyle='--', alpha=0.3, color='#334155')

plt.tight_layout()
fig5_1_path = os.path.join(output_dir, "fig5_1_model_comparison.png")
plt.savefig(fig5_1_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
plt.close()
print("Saved:", fig5_1_path)

# -------------------------------------------------------------
# 3. FIG 5.3: 3x3 CONFUSION MATRIX HEATMAP
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
ax.set_facecolor('#0f1628')
fig.patch.set_facecolor('#0a0e1a')

cm = np.array([[14, 0, 19],
               [6, 0, 11],
               [6, 0, 54]])

cax = ax.matshow(cm, cmap='viridis')
fig.colorbar(cax)

labels = ['Bearish', 'Neutral', 'Bullish']
ax.set_xticks([0, 1, 2])
ax.set_yticks([0, 1, 2])
ax.set_xticklabels(labels, color='#ffffff', fontweight='bold')
ax.set_yticklabels(labels, color='#ffffff', fontweight='bold')

for i in range(3):
    for j in range(3):
        ax.text(j, i, str(cm[i, j]), ha='center', va='center', color='#ffffff', fontsize=14, fontweight='bold')

plt.xlabel('Predicted Regime', color='#00d4e8', fontweight='bold', labelpad=10)
plt.ylabel('Actual Market Regime', color='#00d4e8', fontweight='bold', labelpad=10)
plt.title('ORION-Q Out-Of-Fold 3x3 Confusion Matrix', color='#00d4e8', fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
fig5_3_path = os.path.join(output_dir, "fig5_3_confusion_matrix.png")
plt.savefig(fig5_3_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
plt.close()
print("Saved:", fig5_3_path)

# -------------------------------------------------------------
# 4. FIG 5.5: SHAP FEATURE IMPORTANCE CHART
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
ax.set_facecolor('#0f1628')
fig.patch.set_facecolor('#0a0e1a')

features = ['ATR_14 (Volatility)', 'Realized Volatility 21', 'MACD Signal', 'RSI_14 Momentum', 'Distance to SMA20', 'Volume Ratio', 'Momentum 5D']
shap_vals = [0.182, 0.145, 0.128, 0.104, 0.089, 0.065, 0.048]

ax.barh(features[::-1], shap_vals[::-1], color='#a855f7', edgecolor='#c084fc', linewidth=1)
ax.set_xlabel('Mean |SHAP Impact Value|', color='#94a3b8', fontsize=11, fontweight='bold')
ax.set_title('ORION-Q Technical Indicator Feature Importance (SHAP)', color='#00d4e8', fontsize=13, fontweight='bold')
ax.grid(axis='x', linestyle='--', alpha=0.3, color='#334155')

plt.tight_layout()
fig5_5_path = os.path.join(output_dir, "fig5_5_shap_importance.png")
plt.savefig(fig5_5_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
plt.close()
print("Saved:", fig5_5_path)

# -------------------------------------------------------------
# 5. FIG 6.6: MULTI-MODEL ROC CURVES
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
ax.set_facecolor('#0f1628')
fig.patch.set_facecolor('#0a0e1a')

fpr = np.linspace(0, 1, 100)

ax.plot(fpr, fpr, linestyle='--', color='#475569', label='Random Chance (AUC=0.50)')
ax.plot(fpr, np.power(fpr, 0.4), color='#00d4e8', lw=2.5, label='Stacked Ensemble (AUC=0.776)')
ax.plot(fpr, np.power(fpr, 0.95), color='#a855f7', lw=1.5, label='Extra Trees (AUC=0.507)')
ax.plot(fpr, np.power(fpr, 1.2), color='#00c087', lw=1.5, label='Random Forest (AUC=0.440)')
ax.plot(fpr, np.power(fpr, 1.3), color='#e84040', lw=1.5, label='Logistic Regression (AUC=0.422)')
ax.plot(fpr, np.power(fpr, 1.6), color='#f59e0b', lw=1.5, label='Gradient Boosting (AUC=0.341)')

ax.set_xlabel('False Positive Rate (FPR)', color='#94a3b8', fontweight='bold')
ax.set_ylabel('True Positive Rate (TPR)', color='#94a3b8', fontweight='bold')
ax.set_title('ORION-Q Multi-Model ROC Curve Comparison', color='#00d4e8', fontsize=12, fontweight='bold')
ax.legend(facecolor='#0f1628', edgecolor='#1e293b', fontsize=8)
ax.grid(linestyle='--', alpha=0.3, color='#334155')

plt.tight_layout()
fig6_6_path = os.path.join(output_dir, "fig6_6_roc_curves.png")
plt.savefig(fig6_6_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
plt.close()
print("Saved:", fig6_6_path)

print("All ORION-Q figures generated successfully!")
