from flask import Blueprint, send_file, flash, redirect, url_for, render_template

from models import Employee, Operation

report_routes = Blueprint('reports', __name__)


@report_routes.route('/')
def report_home():
    # Récupérer tous les employés depuis la base de données
    employees = Employee.query.all()
    all_operations_confirmed = Operation.query.filter_by(
        researcher_confirmed=False).count() == 0
    return render_template('reports.html', employees=employees, all_operations_confirmed=all_operations_confirmed)


@report_routes.route('/generate_employee_report/<int:employee_id>')
def employee_report(employee_id):
    from utils.report_utils import generate_employee_report
    try:
        filename = generate_employee_report(employee_id)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('main.index'))


@report_routes.route('/generate_phytosanitary_report')
def phytosanitary_report():
    from utils.report_utils import generate_phytosanitary_report

    try:
        filename = generate_phytosanitary_report()
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('main.index'))
