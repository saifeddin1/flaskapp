from datetime import datetime
import os
import io
from fpdf import FPDF
from models import Operation, Employee
import matplotlib.pyplot as plt
from models import db


class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Annual Summary Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def ensure_reports_directory():
    """
    Vérifie que le dossier 'reports' existe, sinon le crée.
    """
    if not os.path.exists('reports'):
        os.makedirs('reports')


def generate_operation_graph(operations):
    """
    Génère un graphique de la distribution des types d'opérations
    et le sauvegarde dans un fichier temporaire.
    """
    # Récupérer les données pour le graphique
    operation_types = [op.operation_type for op in operations]

    # Compter les occurrences de chaque type d'opération
    type_counts = {}
    for op_type in operation_types:
        type_counts[op_type] = type_counts.get(op_type, 0) + 1

    # Créer le graphique
    fig, ax = plt.subplots()
    ax.bar(type_counts.keys(), type_counts.values())
    ax.set_title("Distribution of Operation Types")
    ax.set_xlabel("Operation Types")
    ax.set_ylabel("Count")

    # Sauvegarder le graphique dans un fichier temporaire
    graph_path = 'reports/temp_graph.png'
    plt.savefig(graph_path, format='png')
    plt.close(fig)

    return graph_path


def generate_annual_summary_report():
    """
    Generates a PDF summary report for the year.
    """
    # Ensure reports directory exists
    if not os.path.exists('reports'):
        os.makedirs('reports')

    # Get current year and all operations
    current_year = datetime.now().year
    operations = Operation.query.filter(db.extract(
        'year', Operation.date) == current_year).all()

    # Aggregate data
    total_operations = len(operations)
    total_employees = Employee.query.count()
    operations_per_employee = {emp.name: 0 for emp in Employee.query.all()}
    for op in operations:
        operations_per_employee[op.employee.name] += 1

    # Generate operation distribution chart
    chart_path = generate_operation_graph(operations)

    # Create the PDF
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    pdf.cell(0, 10, f"Annual Summary Report for {current_year}", 0, 1)
    pdf.ln(5)
    pdf.cell(0, 10, f"Total Operations: {total_operations}", 0, 1)
    pdf.cell(0, 10, f"Total Employees: {total_employees}", 0, 1)
    pdf.ln(5)

    # Add operations per employee
    pdf.cell(0, 10, "Operations Per Employee:", 0, 1)
    for name, count in operations_per_employee.items():
        pdf.cell(0, 10, f"{name}: {count}", 0, 1)

    pdf.ln(10)

    # Add operation distribution chart
    pdf.cell(0, 10, "Operation Distribution Chart:", 0, 1)
    pdf.image(chart_path, x=10, w=180)
    os.remove(chart_path)  # Clean up chart image

    # Save the PDF
    filename = f'reports/annual_summary_{current_year}.pdf'
    pdf.output(filename)
    return filename


def generate_employee_report(employee_id):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    employee = Employee.query.get(employee_id)
    pdf.cell(0, 10, f"Report for Employee: {employee.name}", 0, 1)
    pdf.ln(5)

    operations = Operation.query.filter_by(employee_id=employee_id).all()
    for op in operations:
        pdf.cell(0, 10, f"{op.date}: {op.operation_type}", 0, 1)

    filename = f'reports/employee_{employee_id}.pdf'
    pdf.output(filename)
    return filename


def generate_phytosanitary_report():
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    pdf.cell(0, 10, "Phytosanitary Report", 0, 1)
    pdf.ln(5)

    phytosanitary_ops = Phytosanitary.query.all()
    for op in phytosanitary_ops:
        pdf.cell(
            0, 10, f"Disease: {op.diseases_targeted}, Stage: {op.disease_stage}", 0, 1)
        pdf.cell(
            0, 10, f"Treatment: {op.treatment_methods}, Observations: {op.observations}", 0, 1)
        pdf.ln(5)

    filename = 'reports/phytosanitary_report.pdf'
    pdf.output(filename)
    return filename
