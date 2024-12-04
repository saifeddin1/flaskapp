from datetime import datetime
from flask import Blueprint, abort, render_template, redirect, url_for, request, flash
from flask_login import current_user
from models import Operation, User, db, Employee

from utils.permissions import role_required
from utils.report_utils import generate_annual_summary_report

main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def index():
    return render_template('index.html')


@main_routes.route('/employees', methods=['GET', 'POST'])
def manage_employees():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        if name and role:
            new_employee = Employee(name=name, role=role)
            db.session.add(new_employee)
            db.session.commit()
            flash("Employee added successfully!", "success")
        else:
            flash("Please fill in all fields.", "danger")
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)


@main_routes.route('/delete_employee/<int:id>')
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted successfully!", "success")
    return redirect(url_for('main.manage_employees'))


@role_required('chief')
@main_routes.route('/validate_data', methods=['POST'])
def validate_data():
    from utils.email_utils import send_email

    """
    Valide toutes les opérations pour le mois en cours et envoie un email au chercheur.
    """
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Trouver les opérations du mois en cours
    operations = Operation.query.filter(
        db.extract('month', Operation.date) == current_month,
        db.extract('year', Operation.date) == current_year,
        Operation.validated == False
    ).all()

    if not operations:
        flash("No operations found for the current month to validate.", "warning")
        return redirect(url_for('main.index'))

    # Valider les opérations
    for op in operations:
        op.validated = True
    db.session.commit()

    # Récupérer les emails des chercheurs
    researchers = User.query.filter_by(role='researcher').all()
    researcher_emails = [user.email for user in researchers]

    # Construire le contenu de l'email
    operation_details = [
        f"- {op.date}: {op.operation_type} (Employee: {op.employee.name})" for op in operations]
    body = f"""
    Dear Researcher,

    The monthly data submission for {current_month}/{current_year} has been completed.
    Below is the summary of the validated data:

    Total Validated Operations: {len(operations)}

    Operations:
    {chr(10).join(operation_details)}

    Best regards,
    The Viticulture System
    """

    # Envoyer l'email aux chercheurs
    subject = f"Monthly Data Submission Completed - {current_month}/{current_year}"
    if send_email(subject, researcher_emails, body):
        flash("Data validated and researcher notified successfully!", "success")
    else:
        flash("Data validated but failed to notify the researcher.", "danger")

    return redirect(url_for('main.index'))


@main_routes.route('/send_annual_report', methods=['POST'])
def send_annual_report():
    from utils.email_utils import send_email
    """
    Generates the annual summary report and emails it to all chiefs of exploitation.
    """
    # Ensure only the researcher can access this route
    if not current_user.is_authenticated or current_user.role != 'researcher':
        abort(403)

    # Generate the annual summary report
    filename = generate_annual_summary_report()

    # Get the emails of all chiefs
    chiefs = User.query.filter_by(role='chief').all()
    chief_emails = [chief.email for chief in chiefs]

    if not chief_emails:
        flash("No chiefs found to send the report to.", "danger")
        return redirect(url_for('main.index'))

    # Email the report to all chiefs
    subject = "Annual Summary Report"
    body = """
    Dear Chief,

    The annual summary report has been completed. Please find the attached report for your review.

    Best regards,
    The Researcher
    """
    if send_email(subject, chief_emails, body, attachments=[filename]):
        flash("Annual summary report emailed to all chiefs successfully!", "success")
    else:
        flash("Failed to send the annual summary report.", "danger")

    return redirect(url_for('main.index'))
