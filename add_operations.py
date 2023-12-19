# lecteur csv et affichage des données

import csv
import matplotlib.pyplot as plt
import os


OUTPUT_BEGIN_WITH = "operations_"
MAX_NB_LINES = 4
CSV_FOLDER = "datas"


def setup_lists():
    for file in os.listdir(CSV_FOLDER):
        if file.startswith(OUTPUT_BEGIN_WITH) and file.endswith(".csv"):
            print("lecture du fichier " + os.path.join(CSV_FOLDER,file))
            with open(os.path.join(CSV_FOLDER,file), newline='', encoding='utf-8') as catfile:
                catreader = csv.reader(catfile, delimiter=';', quotechar='|')
                for row in catreader:
                    if (row[1] == "Catégorie"):
                        continue
                    if (row[1] not in cats):
                        cats.append(row[1])
                    if (file == output_file and row[4] not in opsDone):
                        opsDone.append(row[4])

                    libelle_already_exists = any(item[0] == row[0] for item in libellesAlreadyCategorized)

                    if not libelle_already_exists:
                        libellesAlreadyCategorized.append((row[0], row[1]))
                    
                catfile.close()

def create_output_if_not_exists():
    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER)

    if not os.path.exists(os.path.join(CSV_FOLDER,output_file)):
        with open(os.path.join(CSV_FOLDER,output_file), 'a', newline='', encoding="utf-8") as catfile:
            catswriter = csv.writer(catfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            catswriter.writerow(["Libelle", "Catégorie", "Débit", "Crédit", "Référence"])
            catfile.close()

# confirmer l'association d'une catégorie à une opération
def confirm (libelle, ref,debit, credit, cat, cats):
    cat = cat.isdigit() and cats[int(cat)-1] or cat
    cat = cat.upper()

    print("Êtes-vous sur de vouloir associer l'opération \033[4m\033[1m" + libelle + "\033[0m à la catégorie \033[4m\033[1m" + cat + "\033[0m ? (y/n)")
    text = input(">>> ")
    if (text == "y" or text == ""):
        with open(os.path.join(CSV_FOLDER,output_file), 'a', newline='', encoding="utf-8") as catfile:
            catswriter = csv.writer(catfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            catswriter.writerow([libelle, cat, debit, credit, ref])
            catfile.close()
            if (cat not in cats):
                cats.append(cat)

            libelle_already_exists = any(item[0] == cat for item in libellesAlreadyCategorized)

            if not libelle_already_exists:
                libellesAlreadyCategorized.append((libelle, cat))
            
            opsDone.append(ref)

            print("Opération réussie !")

            return True
    else:
        print("Pas de problème, on recommence :)\n")
        return False
    
def ask_file():
    print("Quel tableaux de compte voulez-vous renseigner (.csv) ?")
    file = input(">>> ")
    if (file[-4:] != ".csv"):
        print("Ce fichier n'est pas un tableur. Veuillez renseigner un fichier .csv")
        file = ask_file()
    try :
        open(os.path.join(CSV_FOLDER,file), mode='r', encoding='utf-8', )
    except FileNotFoundError:
        print("Ce fichier n'existe pas. Veuillez renseigner un fichier .csv")
        file = ask_file()
    
    return file

def printCatsInColumns(categories, nbColumns):
    if "+" in categories:
        categories.remove("+")
    if "exit" in categories:
        categories.remove("exit")
    categories.append("+")
    categories.append("exit")
    categories = list(dict.fromkeys(categories))
    nbLignes = (len(categories) + nbColumns - 1) // nbColumns
    for i in range(nbLignes):
        for j in range(nbColumns):
            index = j * nbLignes + i
            if index < len(categories):
                print(print_element(index, categories[index]), end='')
        print()

def print_element(index, item):
    largeur_colonne = 30
    if item == "+":
        return f"[{item}] NOUVELLE CATÉGORIE".ljust(largeur_colonne)
    elif item == "exit":
        return f"[{item}] QUITTER".ljust(largeur_colonne)
    return f"[{index+1}] {item}".ljust(largeur_colonne)

def main_process():
    with open(os.path.join(CSV_FOLDER,name_file_to_read), newline='', encoding='utf-8') as file_to_read:
        spamreader = csv.reader(file_to_read, delimiter=';', quotechar='|')        

        for row in spamreader:
            libelle = row[1]
            ref = row[3]
            debit = row[8]
            credit = row[9]
            if (ref in opsDone):
                continue
            if (libelle == "Libelle simplifie"):
                continue
            confirmed = False
            print("\n------------------------")
            while (not confirmed):
                print("Quelle est la catégorie de l'opération \033[4m\033[1m" + libelle + "\033[0m (" + row[0] + ") ?")

                libelle_trouve = False

                for item in libellesAlreadyCategorized:
                    if libelle == item[0]:
                        libelle_trouve = True
                        categorie = item[1]
                        break

                if libelle_trouve:
                    print(f"Cette opération a déjà été catégorisée. Voulez-vous lui assigner la même catégorie ? (\033[4m\033[1m" + categorie + "\033[0m) (y/n)")
                    text = input(">>> ")
                    if (text == "y" or text == ""):
                        confirmed = confirm(libelle, ref, debit, credit, categorie, cats)
                        continue
                    elif (text == "exit"):
                        print("Au revoir :)")
                        exit()
                
                nbColumns = 1

                while ((len(cats) + 2) / nbColumns > MAX_NB_LINES):
                    nbColumns += 1

                printCatsInColumns(cats, nbColumns)
                cat = input(">>> ")
                if (cat == "+"):
                    print("Quel est le nom de cette nouvelle catégorie ?")
                    cat = input(">>> ")
                elif (cat == "exit"):
                    print("Au revoir :)")
                    exit()
                elif (not cat.isdigit() or int(cat) > len(cats) or int(cat) < 1):
                    print("Cette catégorie n'est pas valide pour l'opération \033[4m\033[1m" + libelle + "\033[0m (" + row[0] + ")")
                    continue
                confirmed = confirm(libelle, ref,debit, credit, cat, cats)
        file_to_read.close()

    
if __name__ == "__main__":
    cats = [] # liste des catégories (ça va chercher dans les fichiers déjà créés qui commencent par OUTPUT_BEGIN_WITH)
    libellesAlreadyCategorized = [] # liste des libellés déjà catégorisés (pour demander si on veut assigner la même catégorie)
    opsDone = [] # liste des références des opérations déjà catégorisées (pour éviter de les refaire)
    name_file_to_read = ask_file()
    output_file = OUTPUT_BEGIN_WITH + name_file_to_read.split(".")[0] + ".csv"

    setup_lists()
    create_output_if_not_exists()
    main_process()
    # test

    print("Toutes les catégories ont été enregistrées :)")
    print("Vous pouvez maintenant lancer le programme 'graph.py' pour avoir une représentation graphique de vos comptes.")
    print("Au revoir :)")


