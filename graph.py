import csv
import matplotlib.pyplot as plt
import os

# operations_data_og.csv
CSV_FOLDER = "datas"
OUTPUT_BEGIN_WITH = "operations_"

def ask_file():
    print("Quel tableaux de compte voulez-vous lire (.csv) ?")
    file = input(">>> " + OUTPUT_BEGIN_WITH)
    file = OUTPUT_BEGIN_WITH + file

    if (file[-4:] != ".csv"):
        print("Ce fichier n'est pas un tableur. Veuillez renseigner un fichier .csv")
        file = ask_file()
    
    try :
        open(os.path.join(CSV_FOLDER,file), mode='r', encoding='utf-8', )
    except FileNotFoundError:
        print("Ce fichier n'existe pas. Veuillez renseigner un fichier .csv")
        file = ask_file()
    
    return file


def read(csvfile):
    categoriesDebits = {}
    categoriesCredits = {}
    with open(os.path.join(CSV_FOLDER,csvfile), mode='r', encoding='utf-8', ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        
        for row in reader:
            categorie = row["Catégorie"]
            debit = row["Débit"].replace(',', '.')

            debit = float(debit) if debit else 0
            debit = -debit if debit < 0 else debit

            if debit != 0:
                if categorie not in categoriesDebits:
                    categoriesDebits[categorie] = 0
                categoriesDebits[categorie] += debit
            else:
                credit = row["Crédit"].replace(',', '.')
                credit = float(credit) if credit else 0
                
                if categorie not in categoriesCredits:
                    categoriesCredits[categorie] = 0
                categoriesCredits[categorie] += credit
        csvfile.close()
    return categoriesDebits, categoriesCredits

def display():
    # Création des listes pour le premier graphique camembert
    labels1 = list(categoriesDebits.keys())
    sizes1 = list(categoriesDebits.values())

    # Création des listes pour le second graphique camembert
    labels2 = list(categoriesCredits.keys())
    sizes2 = list(categoriesCredits.values())

    # Création des graphiques camembert
    plt.figure(figsize=(15, 6))

    plt.subplot(1, 2, 1)  # 1 ligne, 2 colonnes, graphique n°1
    plt.pie(sizes1, labels=labels1, autopct='%1.1f%%')
    plt.title('Répartition des dépenses par catégorie')

    plt.subplot(1, 2, 2)  # 1 ligne, 2 colonnes, graphique n°2
    plt.pie(sizes2, labels=labels2, autopct='%1.1f%%')
    plt.title('Répartition des crédits par catégorie')

    plt.show()

if __name__ == "__main__":
    csvfile = ask_file()
    categoriesDebits, categoriesCredits = read(csvfile)
    display()