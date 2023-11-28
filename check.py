"""Module pour vérifier si les dépendances sont installées"""
import sys
import pkg_resources
from pkg_resources import Requirement

# Fonction pour lire les dépendances depuis le fichier requirements.txt
def read_requirements(file_path):
    """Fonction pour lire les dépendances depuis le fichier requirements.txt"""
    with open(file_path, 'r', encoding=("utf-8")) as file:
        requirements = [line.strip() for line in file]
    return requirements

# Fonction pour vérifier si une dépendance est installée avec la version requise
def is_dependency_installed_with_version(package_spec):
    """Fonction pour vérifier si une dépendance est installée avec la version requise"""
    try:
        requirement = Requirement.parse(package_spec)
        installed_version = pkg_resources.get_distribution(requirement.project_name).version
        return installed_version == requirement.specs[0][1]
    except (pkg_resources.DistributionNotFound, IndexError):
        return False

# Fonction pour vérifier si une dépendance est installée
def is_dependency_installed(package_name):
    """Fonction pour vérifier si une dépendance est installée"""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

# Chemin vers le fichier requirements.txt
REQUIREMENT_FILENAME = 'requirements.txt'

# Lire les dépendances depuis le fichier
required_dependencies = read_requirements(REQUIREMENT_FILENAME)

# Vérifier si chaque dépendance est installée (avec ou sans version spécifiée)
missing_dependencies = []

for dependency in required_dependencies:
    if '==' in dependency:
        if not is_dependency_installed_with_version(dependency):
            missing_dependencies.append(dependency)
    else:
        if not is_dependency_installed(dependency):
            missing_dependencies.append(dependency)

if not missing_dependencies:
    sys.exit(1)
sys.exit(0)
