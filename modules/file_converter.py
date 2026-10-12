"""
File Converter Hub - Excel to PDF and related - SLIM version for Render
Tools:
- Excel (xlsx, xls, csv) to PDF
- CSV to Excel
- Image to PDF
- Excel to CSV
"""

import os
import pandas as pd
from typing import Dict, Any

def excel_to_pdf(excel_path: str, pdf_path: str) -> Dict[str, Any]:
    try:
        if excel_path.lower().endswith('.csv'):
            df = pd.read_csv(excel_path)
            sheets = {"Sheet1": df}
        else:
            xls = pd.ExcelFile(excel_path)
            sheets = {}
            for sheet_name in xls.sheet_names[:5]:
                try:
                    sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
                except:
                    continue

        if not sheets:
            return {"ok": False, "error": "No data found in Excel"}

        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        story = []

        for sheet_name, df in sheets.items():
            if df.empty:
                continue
            df_display = df.head(100)
            df_display = df_display.iloc[:, :15]
            df_display = df_display.fillna("")
            df_display = df_display.astype(str)
            story.append(Paragraph(f"<b>Sheet: {sheet_name}</b> - {len(df)} rows, {len(df.columns)} cols", styles['Heading2']))
            story.append(Spacer(1, 10))
            table_data = [list(df_display.columns)] + df_display.values.tolist()
            for i in range(len(table_data)):
                for j in range(len(table_data[i])):
                    cell = str(table_data[i][j])
                    if len(cell) > 50:
                        table_data[i][j] = cell[:50] + "..."
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#D9E1F2')]),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

        doc.build(story)
        return {"ok": True, "pdf": pdf_path, "sheets": len(sheets), "total_rows": sum(len(df) for df in sheets.values())}
    except Exception as e:
        return {"ok": False, "error": f"Excel to PDF error: {str(e)[:300]}"}

def csv_to_excel(csv_path: str, excel_path: str) -> Dict[str, Any]:
    try:
        df = pd.read_csv(csv_path)
        df.to_excel(excel_path, index=False)
        return {"ok": True, "excel": excel_path, "rows": len(df)}
    except Exception as e:
        return {"ok": False, "error": f"CSV to Excel error: {str(e)[:200]}"}

def excel_to_csv(excel_path: str, csv_path: str) -> Dict[str, Any]:
    try:
        df = pd.read_excel(excel_path)
        df.to_csv(csv_path, index=False)
        return {"ok": True, "csv": csv_path, "rows": len(df)}
    except Exception as e:
        return {"ok": False, "error": f"Excel to CSV error: {str(e)[:200]}"}

def images_to_pdf(image_paths: list, pdf_path: str) -> Dict[str, Any]:
    try:
        from PIL import Image
        images = []
        for img_path in image_paths[:20]:
            img = Image.open(img_path)
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            else:
                img = img.convert("RGB")
            images.append(img)
        if not images:
            return {"ok": False, "error": "No valid images"}
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        return {"ok": True, "pdf": pdf_path, "images": len(images)}
    except Exception as e:
        return {"ok": False, "error": f"Images to PDF error: {str(e)[:200]}"}

def pdf_to_text(pdf_path: str) -> Dict[str, Any]:
    try:
        text = ""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:20]:
                    text += (page.extract_text() or "") + "\n"
        except ImportError:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(pdf_path)
                for page in reader.pages[:20]:
                    text += (page.extract_text() or "") + "\n"
            except ImportError:
                return {"ok": False, "error": "PDF lib not installed. Install pdfplumber or PyPDF2 locally. On Render, PDF to Text disabled to save RAM."}
        return {"ok": True, "text": text[:10000], "chars": len(text)}
    except Exception as e:
        return {"ok": False, "error": f"PDF to Text error: {str(e)[:200]}"}
