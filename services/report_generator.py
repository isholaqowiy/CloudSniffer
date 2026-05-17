import os
from datetime import datetime
from fpdf import FPDF

class ReportGenerator:
    @staticmethod
    def generate_txt_report(report_data: dict, file_path: str) -> str:
        content = (
            f"==================================================\n"
            f"          AI CONTENT DETECTION REPORT             \n"
            f"==================================================\n"
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"Final Verdict: {report_data.get('verdict')}\n"
            f"Confidence Level: {report_data.get('confidence')}\n\n"
            f"PROBABILITY DISTRIBUTION:\n"
            f"[-] AI Generation Probability: {report_data.get('ai_probability')}%\n"
            f"[-] Human Origin Probability: {report_data.get('human_probability')}%\n\n"
            f"ANALYSIS SUMMARY:\n"
        )
        for trace in report_data.get("analysis", []):
            content += f" • {trace}\n"
            
        content += f"\nINSTRUCTOR RECOMMENDATION:\n{report_data.get('recommendation')}\n"
        content += f"==================================================\n"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    @staticmethod
    def generate_pdf_report(report_data: dict, file_path: str) -> str:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "AI Content Detection Report", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Generated On: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", ln=True, align="C")
        pdf.line(10, 32, 200, 32)
        pdf.ln(10)
        
        # Primary Metrics Summary Block
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Final Assessment: {report_data.get('verdict')}", ln=True)
        pdf.cell(0, 8, f"Confidence Rating: {report_data.get('confidence')}", ln=True)
        pdf.ln(4)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Statistical Indicators Matrix:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f" - AI-Sourced Likelihood: {report_data.get('ai_probability')}%", ln=True)
        pdf.cell(0, 7, f" - Human-Sourced Likelihood: {report_data.get('human_probability')}%", ln=True)
        pdf.ln(6)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Forensic Insight Vectors Logged:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for point in report_data.get("analysis", []):
            pdf.multi_cell(0, 6, f" * {point}")
            
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Actionable Instructor Guidance:", ln=True)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 6, str(report_data.get("recommendation")))
        
        pdf.output(file_path)
        return file_path
