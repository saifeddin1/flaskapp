from flask import Blueprint, render_template, Response
import io
import matplotlib.pyplot as plt
from models import Operation

# Déclarer le Blueprint
analysis_routes = Blueprint('analysis', __name__)


@analysis_routes.route('/')
def analysis_page():
    return render_template('analysis.html')


@analysis_routes.route('/plot.png')
def plot_operations():
    # Distribution des types d'opérations
    operations = Operation.query.all()
    operation_types = [op.operation_type for op in operations]

    # Préparer les données pour le graphique
    type_counts = {}
    for op_type in operation_types:
        type_counts[op_type] = type_counts.get(op_type, 0) + 1

    # Générer le graphique
    fig, ax = plt.subplots()
    ax.bar(type_counts.keys(), type_counts.values())
    ax.set_title("Distribution of Operation Types")
    ax.set_xlabel("Operation Types")
    ax.set_ylabel("Count")

    # Sauvegarder dans un flux mémoire
    output = io.BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)

    # Retourner l'image comme réponse HTTP
    return Response(output, mimetype='image/png')
