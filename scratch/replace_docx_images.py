import docx
import os
import shutil

def replace_docx_images(docx_path, output_path, figures_map):
    doc = docx.Document(docx_path)
    
    # Iterate through all image parts in the document package
    image_parts = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_parts.append(rel.target_part)
            
    print(f"Found {len(image_parts)} embedded image stream parts in document.")

    # Map figure indices to image files
    # Replace image bytes directly in target parts
    for idx, (img_name, img_path) in enumerate(figures_map.items()):
        if idx < len(image_parts) and os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                img_bytes = f.read()
            image_parts[idx]._blob = img_bytes
            print(f"Replaced image stream {idx+1} with {img_name} ({len(img_bytes)} bytes).")

    doc.save(output_path)
    print(f"Document figures updated successfully and saved to {output_path}!")

if __name__ == "__main__":
    doc_path = r"C:\Users\praja\Downloads\ORION-Q_PBL_Report_Submission.docx"
    output_path = r"C:\Users\praja\Downloads\ORION-Q_PBL_Report_Final_With_Figures.docx"
    figures_dir = r"c:\Users\praja\Downloads\newml\scratch\figures"
    
    fig_map = {
        "Fig 4.1 Architecture": os.path.join(figures_dir, "fig4_1_architecture.png"),
        "Fig 5.1 Model Comparison": os.path.join(figures_dir, "fig5_1_model_comparison.png"),
        "Fig 5.3 Confusion Matrix": os.path.join(figures_dir, "fig5_3_confusion_matrix.png"),
        "Fig 5.5 SHAP Importance": os.path.join(figures_dir, "fig5_5_shap_importance.png"),
        "Fig 6.6 ROC Curves": os.path.join(figures_dir, "fig6_6_roc_curves.png")
    }
    
    replace_docx_images(doc_path, output_path, fig_map)
