import csv
import os
from config import config

OUTPUT_BEGIN_WITH = config["output_begin_with"]
MAX_NB_LINES = 4
CSV_FOLDER = config["csv_folder"]
CSV_DELIMITER = config["csv_delimiter"]   
ADD_CAT_SIGN = "+"
MODIFY_CAT_SIGN = "m"
EXIT_SIGN = "q"
ASK_BEFORE_WRITE_ALREADY_EXISTING_LIBELLE = config["ask_before_write_already_existing_libelle"]

# Séquences ANSI pour les couleurs et les styles
RED = "\033[31m"  # Rouge
GREEN = "\033[32m"  # Vert
BLUE = "\033[34m"  # Bleu
BOLD = "\033[1m"  # Gras
UNDERLINE = "\033[4m"  # Souligné
RESET = "\033[0m"  # Réinitialise le style

# ces listes sont alimentées pendant l'exécution du programme, 
# mais aussi au lancement du programme (en allant chercher dans les fichiers déjà créés qui commencent par OUTPUT_BEGIN_WITH)
cats = [] # liste des catégories
libellesAlreadyCategorized = [] # liste des libellés déjà catégorisés (pour demander si on veut assigner la même catégorie)
opsDone = [] # liste des références des opérations déjà catégorisées (pour éviter de les refaire)

output_filename = None # nom du fichier de sortie
source_filename = None # nom du fichier à lire

def setup_lists():
    global cats
    global libellesAlreadyCategorized
    global opsDone
    for file in os.listdir(CSV_FOLDER):
        if file.startswith(OUTPUT_BEGIN_WITH) and file.endswith(".csv"):
            with open(os.path.join(CSV_FOLDER,file), newline='', encoding='utf-8') as output_file:
                catreader = csv.reader(output_file, delimiter=CSV_DELIMITER, quotechar='|')
                for row in catreader:
                    if row[1] == "Catégorie":
                        continue
                    if row[1] not in cats:
                        cats.append(row[1])
                    if file == output_filename and row[4] not in opsDone:
                        opsDone.append(row[4])

                    libelle_already_exists = any(item[0] == row[0] for item in libellesAlreadyCategorized)

                    if not libelle_already_exists:
                        libellesAlreadyCategorized.append((row[0], row[1]))

def create_output_if_not_exists():
    global output_filename

    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER)

    if not os.path.exists(os.path.join(CSV_FOLDER,output_filename)):
        with open(os.path.join(CSV_FOLDER,output_filename), 'a', newline='', encoding="utf-8") as output_file:
            catswriter = csv.writer(output_file, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            catswriter.writerow(["Libelle", "Catégorie", "Débit", "Crédit", "Référence"])

# confirmer l'association d'une catégorie à une opération
def confirm (libelle, ref,debit, credit, cat):
    cat = cat.upper()

    print("Êtes-vous sur de vouloir associer l'opération \033[4m\033[1m" + libelle + "\033[0m à la catégorie \033[4m\033[1m" + cat + "\033[0m ? (y/n)")
    text = input(">>> ")
    if text == "y" or text == "":
        write_op(libelle, cat, debit, credit, ref)
        print(f"{GREEN}Opération réussie !{RESET}")

        return True
    else:
        print("Pas de problème, on recommence :)\n")
        return False
    
def write_op(libelle, cat, debit, credit, ref):
    global opsDone
    global libellesAlreadyCategorized
    global output_filename
    # in csv file
    with open(os.path.join(CSV_FOLDER,output_filename), 'a', newline='', encoding="utf-8") as output_file:
        catswriter = csv.writer(output_file, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        catswriter.writerow([libelle, cat, debit, credit, ref])
    # in local lists
    if cat not in cats:
        cats.append(cat)
    libelle_already_exists = any(item[0] == cat for item in libellesAlreadyCategorized)
    if not libelle_already_exists:
        libellesAlreadyCategorized.append((libelle, cat))
    opsDone.append(ref)

def ask_file():
    print("Quel tableaux de compte voulez-vous renseigner (.csv) ?")
    file = input(">>> ")
    if file[-4:] != ".csv":
        print(f"Ce fichier {RED}n'est pas un tableur.{RESET} Veuillez renseigner un fichier .csv")
        file = ask_file()
    try :
        open(os.path.join(CSV_FOLDER,file), mode='r', encoding='utf-8', )
    except FileNotFoundError:
        print(f"Ce fichier {RED}n'existe pas.{RESET} Veuillez renseigner un fichier .csv")
        file = ask_file()
    return file

# modifie le nom de la catégorie dans tous les fichiers, 
def modify_cat(cat):
    print("Quel est le nouveau nom de cette catégorie ?")
    new_cat = input(">>> ")
    if new_cat == "":
        print(f"{RED}Le nom de votre catégorie est vide, on recommence.{RESET}")
        return False
    new_cat = new_cat.upper()

    # remplace dans tous les fichiers
    for file in os.listdir(CSV_FOLDER):
        if file.startswith(OUTPUT_BEGIN_WITH) and file.endswith(".csv"):
            with open(os.path.join(CSV_FOLDER,file), newline='', encoding='utf-8') as output_file:
                catreader = csv.reader(output_file, delimiter=CSV_DELIMITER, quotechar='|')
                rows = list(catreader)
                for row in rows:
                    if row[1] == "Catégorie":
                        continue
                    if row[1] == cat:
                        row[1] = new_cat
                with open(os.path.join(CSV_FOLDER,file), 'w', newline='', encoding='utf-8') as output_file:
                    catwriter = csv.writer(output_file, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    catwriter.writerows(rows)
    
    # remplace dans la liste des catégories
    global cats
    for i in range(len(cats)):
        if cats[i] == cat:
            cats[i] = new_cat
    cats = list(dict.fromkeys(cats))
    
    # remplace dans la liste des libellés déjà catégorisés
    global libellesAlreadyCategorized
    for i in range(len(libellesAlreadyCategorized)):
        if libellesAlreadyCategorized[i][1] == cat:
            libellesAlreadyCategorized[i] = (libellesAlreadyCategorized[i][0], new_cat)
            
    
    print(f"{GREEN}Catégorie modifiée !{RESET}")
    return True
    
def printCatsInColumns(categories, nbColumns):
    local_cats = categories.copy()
    if ADD_CAT_SIGN in local_cats:
        local_cats.remove(ADD_CAT_SIGN)
    if MODIFY_CAT_SIGN in local_cats:
        local_cats.remove(MODIFY_CAT_SIGN)
    if EXIT_SIGN in local_cats:
        local_cats.remove(EXIT_SIGN)
    
    local_cats.append(ADD_CAT_SIGN)
    local_cats.append(MODIFY_CAT_SIGN)
    local_cats.append(EXIT_SIGN)
   
    local_cats = list(dict.fromkeys(local_cats))
    nbLignes = (len(local_cats) + nbColumns - 1) // nbColumns
    for i in range(nbLignes):
        for j in range(nbColumns):
            index = j * nbLignes + i
            if index < len(local_cats):
                print(print_element(index, local_cats[index]), end='')
        print()

def print_element(index, item):
    largeur_colonne = 30
    if item == ADD_CAT_SIGN:
        return f"{GREEN}[{item}] AJOUTER UNE CATÉGORIE{RESET}".ljust(largeur_colonne)
    elif item == MODIFY_CAT_SIGN:
        return f"{BLUE}[{item}] MODIFIER UNE CATÉGORIE{RESET}".ljust(largeur_colonne)
    elif item == EXIT_SIGN:
        return f"{RED}[{item}] QUITTER{RESET}".ljust(largeur_colonne)
    
    return f"[{index+1}] {item}".ljust(largeur_colonne)

def main_process():
    global cats
    global libellesAlreadyCategorized
    global opsDone
    global source_filename

    
    with open(os.path.join(CSV_FOLDER,source_filename), newline='', encoding='utf-8') as file_to_read:
        spamreader = csv.reader(file_to_read, delimiter=CSV_DELIMITER, quotechar='|')        
        for row in spamreader:
            libelle = row[1]
            ref = row[3]
            debit = row[8]
            credit = row[9]
            if ref in opsDone:
                continue
            if libelle == "Libelle simplifie":
                continue
            confirmed = False
            
            while not confirmed:
                cats.sort()
                print("\n------------------------")
                print("Quelle est la catégorie de l'opération \033[4m\033[1m" + libelle + "\033[0m (" + row[0] + ") ?")

                libelle_trouve = False

                for item in libellesAlreadyCategorized:
                    if libelle == item[0]:
                        libelle_trouve = True
                        categorie = item[1]
                        break

                if libelle_trouve:
                    if ASK_BEFORE_WRITE_ALREADY_EXISTING_LIBELLE:
                        print(f"Cette opération a déjà été catégorisée. Voulez-vous lui assigner la même catégorie ? (\033[4m\033[1m" + categorie + "\033[0m) (y/n)")
                        text = input(">>> ")
                        if text == "y" or text == "":
                            confirmed = confirm(libelle, ref, debit, credit, categorie, cats)
                            continue
                        elif text == EXIT_SIGN:
                            print("Au revoir :)")
                            exit()
                    else:
                        write_op(libelle, categorie, debit, credit, ref)
                        print(f'{GREEN}L\'opération {BOLD}{UNDERLINE}{libelle}{RESET}{GREEN} a été automatiquement classé dans la catégorie {BOLD}{UNDERLINE}{categorie}{RESET}{GREEN}{RESET}')
                        confirmed = True
                        continue
                
                nbColumns = 1
                while ((len(cats) + 3) / nbColumns > MAX_NB_LINES):
                    nbColumns += 1
                printCatsInColumns(cats, nbColumns)

                cat = input(">>> ")
                if cat == ADD_CAT_SIGN:
                    print("Quel est le nom de cette nouvelle catégorie ?")
                    cat = input(">>> ")
                    if cat == "":
                        formatted_text = f"{RED}Le nom de votre catégorie est vide, on recommence.{RESET}"
                        print(formatted_text)
                        continue
                elif cat == EXIT_SIGN:
                    print("Au revoir :)")
                    exit()
                elif cat == MODIFY_CAT_SIGN:
                    is_modified = False
                    while not is_modified:
                        to_modify = input("Quelle catégorie voulez-vous modifier ? (tapez le nom de la catégorie)\n>>> ")
                        if to_modify == "":
                            print(f"{RED}Le nom de votre catégorie est vide, on recommence.{RESET}")
                            continue
                        if to_modify not in cats:
                            print(f"{RED}Cette catégorie n'existe pas.{RESET}")
                            continue
                        is_modified = modify_cat(to_modify)
                    continue
                elif cat.isdigit() and int(cat) <= len(cats) and int(cat) > 0:
                    cat = cats[int(cat)-1]
                else:
                    print(f"{RED}Cette catégorie n'est pas valide pour l'opération {BOLD}{UNDERLINE}{libelle}{RESET}{RED} (30/11/2023){RESET}")
                    continue
                
                confirmed = confirm(libelle, ref,debit, credit, cat)
                
def init_filenames():
    global output_filename
    global source_filename
    source_filename = ask_file()
    output_filename = OUTPUT_BEGIN_WITH + source_filename[0:-4] + ".csv"
 
if __name__ == "__main__":
    init_filenames()
    setup_lists()
    create_output_if_not_exists()
    main_process()

    print ("=========================")
    print("Toutes les catégories ont été enregistrées :)")
    print("Vous pouvez maintenant lancer le programme 'graph.py' pour avoir une représentation graphique de vos comptes.")
    print("Au revoir :)")


