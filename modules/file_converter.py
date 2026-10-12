"""
File Converter - Slim version - optional pandas/reportlab
If libs missing, returns error message instead of crashing
"""

def excel_to_pdf(excel_path, pdf_path):
    try:
        import pandas as pd
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError as e:
        return {"ok": False, "error": f"Excel to PDF requires pandas+reportlab. Install locally: pip install pandas reportlab openpyxl. On Render slim, this tool disabled. Missing: {e}"}

    try:
        if excel_path.lower().endswith('.csv'):
            df = pd.read_csv(excel_path)
            sheets = {"Sheet1": df}
        else:
            xls = pd.ExcelFile(excel_path)
            sheets = {}
            for sheet_name in xls.sheet_names[:3]:
                try:
                    sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
                except:
                    continue
        if not sheets:
            return {"ok": False, "error": "No data in Excel"}

        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        story = []
        for sheet_name, df in sheets.items():
            if df.empty:
                continue
            df_display = df.head(80)
            df_display = df_display.iloc[:, :12]
            df_display = df_display.fillna("").astype(str)
            story.append(Paragraph(f"<b>Sheet: {sheet_name}</b> - {len(df)} rows", styles['Heading2']))
            story.append(Spacer(1, 10))
            table_data = [list(df_display.columns)] + df_display.values.tolist()
            for i in range(len(table_data)):
                for j in range(len(table_data[i])):
                    cell = str(table_data[i][j])
                    if len(cell) > 40:
                        table_data[i][j] = cell[:40] + "..."
            from reportlab.platypus import Table
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        doc.build(story)
        return {"ok": True, "pdf": pdf_path, "sheets": len(sheets), "total_rows": sum(len(df) for df in sheets.values())}
    except Exception as e:
        return {"ok": False, "error": f"Excel to PDF error: {str(e)[:300]}"}

def csv_to_excel(csv_path, excel_path):
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        df.to_excel(excel_path, index=False)
        return {"ok": True, "excel": excel_path, "rows": len(df)}
    except ImportError:
        return {"ok": False, "error": "Requires pandas+openpyxl"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

def excel_to_csv(excel_path, csv_path):
    try:
        import pandas as pd
        df = pd.read_excel(excel_path)
        df.to_csv(csv_path, index=False)
        return {"ok": True, "csv": csv_path, "rows": len(df)}
    except ImportError:
        return {"ok": False, "error": "Requires pandas+openpyxl"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

def images_to_pdf(image_paths, pdf_path):
    try:
        from PIL import Image
        images = []
        for img_path in image_paths[:15]:
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
        return {"ok": False, "error": str(e)[:200]}

def pdf_to_text(pdf_path):
    return {"ok": False, "error": "PDF to Text disabled on Render slim to save RAM. Install pdfplumber locally for this feature."}
