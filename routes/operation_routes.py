from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from datetime import datetime

from flask_login import current_user  # Pour gérer les dates
from models import User, db, Operation, Employee


operation_routes = Blueprint('operations', __name__)


@operation_routes.route('/')
def manage_operations():
    employees = Employee.query.all()
    operations = Operation.query.all()
    all_operations_confirmed = Operation.query.filter_by(
        researcher_confirmed=False).count() == 0
    return render_template('operations.html', employees=employees, operations=operations, all_operations_confirmed=all_operations_confirmed)


@operation_routes.route('/add', methods=['POST'])
def add_operation():
    from utils.email_utils import send_email
    operation_type = request.form.get('operation_type')
    # Récupérer la date sous forme de chaîne
    date_str = request.form.get('date')
    employee_id = request.form.get('employee_id')

    try:
        # Convertir la date en objet datetime.date
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_operation = Operation(
            operation_type=operation_type,
            date=date,
            employee_id=employee_id
        )

        # Si l'opération est de type phytosanitaire, ajouter des données spécifiques
        if operation_type.lower() == 'phytosanitary':
            from models import Phytosanitary
            phytosanitary = Phytosanitary(
                diseases_targeted=request.form.get('diseases_targeted'),
                disease_stage=request.form.get('disease_stage'),
                treatment_methods=request.form.get('treatment_methods'),
                observations=request.form.get('observations')
            )
            db.session.add(phytosanitary)
            db.session.commit()  # Committer pour obtenir l'ID du phytosanitaire
            new_operation.phytosanitary_id = phytosanitary.id

        db.session.add(new_operation)
        db.session.commit()

        # Notify researchers by email
        researchers = User.query.filter_by(role='researcher').all()
        researcher_emails = [researcher.email for researcher in researchers]

        subject = "New Operation Added"
        body = f"""
        Dear Researcher,

        A new operation has been added:
        - Type: {operation_type}
        - Date: {date}

        Please log in to review the operations.

        Best regards,
        The Viticulture System
        """
        if send_email(subject, researcher_emails, body):
            flash("Operation added successfully and researcher notified.", "success")
        else:
            flash(
                "Operation added successfully, but failed to notify the researcher.", "warning")

    except Exception as e:
        flash(f"Error adding operation: {e}", "danger")

    return redirect(url_for('operations.manage_operations'))


@operation_routes.route('/edit/<int:operation_id>', methods=['GET', 'POST'])
def edit_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)
    employees = Employee.query.all()

    if request.method == 'POST':
        operation.operation_type = request.form.get('operation_type')
        date_str = request.form.get('date')
        operation.employee_id = request.form.get('employee_id')

        try:
            # Convertir la date en objet datetime.date
            operation.date = datetime.strptime(date_str, '%Y-%m-%d').date()

            db.session.commit()
            flash("Operation updated successfully!", "success")
            return redirect(url_for('operations.manage_operations'))
        except Exception as e:
            flash(f"Error updating operation: {e}", "danger")

    return render_template('edit_operation.html', operation=operation, employees=employees)


@operation_routes.route('/delete/<int:operation_id>', methods=['POST'])
def delete_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)

    try:
        db.session.delete(operation)
        db.session.commit()
        flash("Operation deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting operation: {e}", "danger")

    return redirect(url_for('operations.manage_operations'))


@operation_routes.route('/confirm', methods=['POST'])
def confirm_operations():
    from utils.email_utils import send_email
    """
    Confirms all operations and notifies chiefs by email.
    """
    # Only researchers can confirm operations
    if not current_user.is_authenticated or current_user.role != 'researcher':
        abort(403)

    # Mark operations as confirmed
    operations = Operation.query.filter_by(researcher_confirmed=False).all()
    for operation in operations:
        operation.researcher_confirmed = True

    db.session.commit()

    # Notify chiefs by email
    chiefs = User.query.filter_by(role='chief').all()
    chief_emails = [chief.email for chief in chiefs]

    subject = "Operations Confirmed by Researcher"
    body = """
    Dear Chief,

    The researcher has reviewed and confirmed all operations for the current period.
    Please log in to generate the required reports.

    Best regards,
    The Viticulture System
    """
    if send_email(subject, chief_emails, body):
        flash("Operations confirmed and chiefs notified successfully!", "success")
    else:
        flash("Operations confirmed, but failed to notify chiefs.", "warning")

    return redirect(url_for('operations.manage_operations'))
