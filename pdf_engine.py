# pdf_engine.py - AstroCaterpillar One-Pager PDF Engine
import io
import re
import base64
from datetime import datetime
from weasyprint import HTML
import matplotlib.pyplot as plt

def _fig_to_base64(fig) -> str:
    """Μετατρέπει ένα Matplotlib figure σε base64 PNG URI."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=180, facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"

def create_astrology_pdf(
    report_title: str,
    profile_name: str,
    details_str: str,
    fig_mat=None,
    summary_info: str = "",
    ai_summary_text: str = "",
    lang: str = "el"
) -> bytes:
    """Δημιουργεί ένα One-Pager Executive Summary PDF χρησιμοποιώντας WeasyPrint."""
    
    chart_img_html = ""
    if fig_mat is not None:
        img_uri = _fig_to_base64(fig_mat)
        chart_img_html = f'<div class="chart-container"><img src="{img_uri}" alt="Astrological Chart" /></div>'

    # Μετατροπή Markdown τίτλων/bolds σε HTML
    formatted_ai_text = ai_summary_text if ai_summary_text else ""
    formatted_ai_text = re.sub(r'###\s*(.*)', r'<h3>\1</h3>', formatted_ai_text)
    formatted_ai_text = re.sub(r'##\s*(.*)', r'<h2>\1</h2>', formatted_ai_text)
    formatted_ai_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_ai_text)
    formatted_ai_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_ai_text)
    formatted_ai_text = formatted_ai_text.replace('\n', '<br/>')

    # Διγλωσσικές ετικέτες
    lbl_profile = "Προφίλ" if lang == "el" else "Profile"
    lbl_date = "Ημ/νία Εξαγωγής" if lang == "el" else "Export Date"
    lbl_indicators = "Βασικοί Δείκτες & Στοιχεία" if lang == "el" else "Core Metrics & Indicators"
    lbl_summary = "Σύνοψη Ανάλυσης AstroCaterpillar" if lang == "el" else "AstroCaterpillar Summary"
    lbl_footer = "AstroCaterpillar AI — Αποκλειστικά για προσωπική χρήση" if lang == "el" else "AstroCaterpillar AI — Strictly for personal use"

    # Πίνακας δεικτών
    table_rows_html = ""
    if summary_info:
        for line in summary_info.split('\n'):
            line_str = line.strip()
            if not line_str:
                continue
            if ':' in line_str:
                k, v = line_str.split(':', 1)
                table_rows_html += f"<tr><td class='key'><strong>{k.strip()}</strong></td><td>{v.strip()}</td></tr>"
            else:
                table_rows_html += f"<tr><td colspan='2'>{line_str}</td></tr>"

    indicators_block = ""
    if table_rows_html:
        indicators_block = f"""
        <h2>{lbl_indicators}</h2>
        <table class="metrics-table">
            {table_rows_html}
        </table>
        """

    export_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <title>{report_title}</title>
        <style>
            *, *::before, *::after {{
                box-sizing: border-box;
            }}
            @page {{
                size: A4;
                margin: 15mm 12mm;
                background-color: #121824;
            }}
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                color: #e2e8f0;
                line-height: 1.5;
                font-size: 10pt;
            }}
            .header {{
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }}
            h1 {{
                font-size: 20pt;
                margin: 0 0 5px 0;
                color: #60a5fa;
                letter-spacing: -0.5px;
            }}
            .subtitle {{
                font-size: 8.5pt;
                color: #94a3b8;
            }}
            .chart-container {{
                text-align: center;
                margin: 15px 0;
            }}
            .chart-container img {{
                max-width: 250px;
                height: auto;
            }}
            h2 {{
                font-size: 12pt;
                color: #93c5fd;
                border-left: 4px solid #3b82f6;
                padding-left: 8px;
                margin-top: 15px;
                margin-bottom: 8px;
                page-break-after: avoid;
            }}
            h3 {{
                font-size: 10.5pt;
                color: #bfdbfe;
                margin-top: 10px;
                margin-bottom: 4px;
                page-break-after: avoid;
            }}
            .metrics-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
                background-color: #1e293b;
                border-radius: 6px;
                overflow: hidden;
            }}
            .metrics-table td {{
                padding: 6px 10px;
                border-bottom: 1px solid #334155;
                font-size: 9pt;
            }}
            .metrics-table td.key {{
                width: 35%;
                color: #cbd5e1;
            }}
            .summary-block {{
                background-color: #1e293b;
                padding: 12px 15px;
                border-radius: 6px;
                border: 1px solid #334155;
            }}
            .footer {{
                text-align: center;
                font-size: 7.5pt;
                color: #64748b;
                margin-top: 20px;
                border-top: 1px solid #334155;
                padding-top: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{report_title}</h1>
            <div class="subtitle">
                <strong>{lbl_profile}:</strong> {profile_name} | {details_str} | <em>{lbl_date}: {export_time}</em>
            </div>
        </div>

        {chart_img_html}
        {indicators_block}

        <h2>{lbl_summary}</h2>
        <div class="summary-block">
            {formatted_ai_text}
        </div>

        <div class="footer">
            {lbl_footer}
        </div>
    </body>
    </html>
    """

    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    return pdf_buffer.getvalue()
  
