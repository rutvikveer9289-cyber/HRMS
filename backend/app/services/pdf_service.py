"""
PDF Service
Generate payslip PDFs using ReportLab
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
import json
from decimal import Decimal

class PDFService:
    """Handles PDF generation for payslips"""
    
    def generate_payslip(self, payroll_record, employee_data) -> BytesIO:
        """
        Generate payslip PDF matching user's requested structure
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom Styles
        company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, fontName='Helvetica-Bold')
        slip_title_style = ParagraphStyle('SlipTitle', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, fontName='Helvetica')
        label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, fontName='Helvetica')
        value_style = ParagraphStyle('Value', parent=styles['Normal'], fontSize=10, fontName='Helvetica')
        table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')
        
        # 1. Header (Company Name & Title)
        header_data = [
            [Paragraph("RBIS TECH SOLUTIONS PVT LTD", company_style)], # Replace with dynamic if needed
            [Paragraph(f"Salary slip for {self._get_month_name(payroll_record.month)} {payroll_record.year}", slip_title_style)]
        ]
        header_table = Table(header_data, colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(header_table)
        
        # 2. Employee Info Section
        emp_info_data = [
            ["Name", f": {employee_data.get('full_name', 'N/A')}", "Department", f": {employee_data.get('department', 'N/A')}"],
            ["Designation", f": {employee_data.get('designation', 'N/A')}", "Bank Name", f": {employee_data.get('bank_name', 'N/A')}"],
            ["Location", f": {employee_data.get('location', 'N/A')}", "Bank Account No.", f": {employee_data.get('bank_account_no', 'N/A')}"]
        ]
        emp_info_table = Table(emp_info_data, colWidths=[1.2*inch, 2.55*inch, 1.25*inch, 2.5*inch])
        emp_info_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(emp_info_table)
        # elements.append(Spacer(1, 0)) # No spacer between boxes as per image
        
        # 3. Earnings and Deductions Tables (Side by Side)
        
        # --- Earnings Data ---
        earnings = [
            [Paragraph("Serial No.", table_header_style), Paragraph("Salary Head", table_header_style), Paragraph("Amount (Rs.)", table_header_style)],
            ["1", "Basic", f"{float(payroll_record.basic_salary):,.0f}"],
            ["2", "Dearness Allowance", f"{float(payroll_record.dearness_allowance):,.0f}"],
            ["3", "House Rent Allowance", f"{float(payroll_record.hra):,.0f}"],
            ["4", "Conveyance Allowance", f"{float(payroll_record.transport_allowance or 0):,.0f}"],
            ["5", "Medical Allowance", f"{float(payroll_record.medical_allowance or 0):,.0f}"],
            ["6", "Special Allowance", f"{float(payroll_record.special_allowance):,.0f}"],
            ["7", "Other Allowance", f"{float(payroll_record.other_allowances):,.0f}"]
        ]
        
        # --- Deductions Data ---
        deductions_raw = json.loads(payroll_record.deduction_details or "[]")
        deductions = [[Paragraph("Serial No.", table_header_style), Paragraph("Salary Head", table_header_style), Paragraph("Amount (Rs.)", table_header_style)]]
        for i, ded in enumerate(deductions_raw, 1):
            deductions.append([str(i), ded['name'], f"{float(ded['amount']):,.0f}"])
        
        # Fill empty rows to align heights if needed (optional)
        while len(deductions) < len(earnings):
            deductions.append(["", "", ""])
        while len(earnings) < len(deductions):
            earnings.append(["", "", ""])
            
        # Create Tables
        e_table = Table(earnings, colWidths=[0.8*inch, 1.9*inch, 1.05*inch])
        d_table = Table(deductions, colWidths=[0.6*inch, 1.9*inch, 1.25*inch])
        
        table_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,1), (0,-1), 'CENTER'), # Serial alignment
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),  # Amount alignment
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ])
        e_table.setStyle(table_style)
        d_table.setStyle(table_style)
        
        # Main Container for Ear/Ded
        main_body_data = [
            [Paragraph("Earnings", table_header_style), Paragraph("Deductions", table_header_style)],
            [e_table, d_table]
        ]
        main_body_table = Table(main_body_data, colWidths=[3.75*inch, 3.75*inch])
        main_body_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(main_body_table)
        elements.append(Spacer(1, 20))
        
        # 4. Final Totals Section
        summary_style = TableStyle([
            ('GRID', (0,0), (1,-1), 0.5, colors.black),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ])
        
        # Left side summary items
        left_summary = [
            ["SALARY (GROSS) / PM", f"{float(payroll_record.gross_salary):,.0f}"],
            ["Reimbursement", "-"],
            ["SALARY (CTC) / PM", f"{float(payroll_record.gross_salary):,.0f}"],
            ["NET SALARY", f"{float(payroll_record.net_salary):,.0f}"],
            ["TOTAL NUMBER OF DAYS", str(payroll_record.working_days or 0)]
        ]
        
        # Right side summary items
        right_summary = [
            ["TOTAL DEDUCTION", f"{float(payroll_record.total_deductions or 0):,.0f}"]
        ]
        
        left_summary_table = Table(left_summary, colWidths=[1.8*inch, 1.4*inch])
        left_summary_table.setStyle(summary_style)
        
        right_summary_table = Table(right_summary, colWidths=[2.0*inch, 1.4*inch])
        right_summary_table.setStyle(summary_style)
        
        summary_container_data = [
            [left_summary_table, Spacer(1,1), right_summary_table]
        ]
        summary_container_table = Table(summary_container_data, colWidths=[3.2*inch, 0.9*inch, 3.4*inch])
        summary_container_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(summary_container_table)

        # Build
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _get_month_name(self, month: int) -> str:
        """Get month name from number"""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return months[month - 1] if 1 <= month <= 12 else "Unknown"
