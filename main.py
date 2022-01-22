#!/usr/bin/python3

#Author: Maël Chouteau
from bs4 import BeautifulSoup
import requests
import sys
import re
import datetime
from httplib2 import Http
import os
import argparse
import mysql.connector
#Générez les api google agenda avant toute chose: https://developers.google.com/calendar/quickstart/python
#Editez les champs ci-dessous:
SERVER = "localhost"
USER = "alcuinsgod"
PASSWORD = "!mad3Alcu1mybitch"
DATABASE = "Notes"

mydb = mysql.connector.connect(host=SERVER, user=USER,password=PASSWORD, database=DATABASE)
print("[*] Connecté à la BDD")
cursor = mydb.cursor() # to access field as dictionary use cursor(as_dict=True)

LOGIN=""
PASS=""
def main(argv):
    #parser = argparse.ArgumentParser(description="Synchronise Alcuin sur Google Agenda")
    #parser.add_argument('days', type=int, help="Nombre de jours a synchroniser")
    #parser.add_argument('-o', '--output', help="Fichier de log")
    #parser.add_argument('date', type=int, nargs='?', const=0, default=0, help="Nombre de jours depuis lequels on synchronise")
    
    #args = parser.parse_args()

    #if args.output:
     #   sys.stdout = open(args.output, 'w+')


    print("[*] Connexion à Alcuin")
    data, session = getInputs("https://esaip.alcuin.com/OpDotNet/Noyau/Login.aspx")
    session = loginAlcuin("https://esaip.alcuin.com/OpDotNet/Noyau/Login.aspx", data, session)  #Connexion successful
    print("[*] Extraction des données et création du tableau")
    #retrieveNotes("", session)
    #IDtoNom(session)
    #retrieveMatiere(session)
    print("[*] Notes synchronisé!")

def getInputs(url): #Get the inputs to send back to the login page (Tokens etc)
    s = requests.Session()
    r = s.get(url)

    soup = BeautifulSoup(r.text, "html.parser")
    inputs = soup.find_all("input")

    data={}
    for i in inputs:    #Extract inputs and store them in data
        try:
            data[i["name"]]=i["value"]
        except:
            pass
    return(data, s)

def loginAlcuin(url,data,s):    #login
    data["UcAuthentification1$UcLogin1$txtLogin"] = LOGIN
    data["UcAuthentification1$UcLogin1$txtPassword"] = PASS
    try:
        s.post(url, data=data)
        print("[*] Connexion à Alcuin réussie")
    except:
        print("[-] Impossible de se connecter à Alcuin")
        sys.exit()
    return(s)

def retrieveNotes(url, s):
    r = s.get('https://esaip.alcuin.com/OpDotNet/Context/context.jsx')  #Get user ID to show the right calendar
    usrId = re.search('\w+[0-9]', r.text).group(0)  #Regex to extract user ID
    #data = {'IdApplication': '190', 'TypeAcces': 'Utilisateur', 'url': '/EPlug/Agenda/Agenda.asp', 'session_IdCommunaute': '561', 'session_IdUser': usrId, 'session_IdGroupe': '786', 'session_IdLangue': '1'}
    #f = s.post("https://esaip.alcuin.com/commun/aspxtoasp.asp", data=data)  #Retrieve the calendar and create the necessary token
    #r = s.post("https://esaip.alcuin.com/EPlug/Agenda/Agenda.asp", data={"NumDat": 20220119, "DebHor": "08", "FinHor": "18", "ValGra": "60", "NomCal":"PRJ13230", "TypVis":"Vis-Jrs.xsl"}) #Extract a specific day
    s.get('https://esaip.alcuin.com/OpDotNet/Eplug/Annuaire/Accueil.aspx?IdApplication=142&TypeAcces=MaFiche&IdLien=6816') #Get obligatoir pour accéder au get suivant
    GObjet = s.get('https://esaip.alcuin.com/OpDotNet/Eplug/Annuaire/Navigation/Dossier/Dossier.aspx').text # Get pour que le serveur nous renvoie le GObjet qui change tous le temps
    GObjet = GObjet[GObjet.index('GObjet=')+len('GObjet='):GObjet.index('&IdObjet')] # Dans la réponse du Get précedant on extrait le code GObjet
    g = s.get('https://esaip.alcuin.com/OpDotNet/Noyau/Utils/LaunchAppli.aspx?IdApplication=142&TypeAcces=MaFiche&groupe=&TypeAppli=0&url=%2fOpDotNet%2fEplug%2fFPC%2fProcess%2fAnnuaire%2fParcours%2fParcours.aspx%3fGObjet%3d'+GObjet+'%26IdObjet%3d'+usrId+'%26IdTypeObjet%3d26%26intIdUtilisateur%3d'+usrId+'%26IdOnglet%3d178%26IdAnnDos%3d6449') # Get qui nous renvoie le post a réaliser (quand on clique sur l'onglet parcour)
    soup = BeautifulSoup(g.text, "html.parser")
    IdSession = soup.find(attrs={"name": "IdSession"} )
    data = {'dUser' : usrId, 'IdCommunity' : '561', 'Idgroupe' : '', 'groupe' : '', 'IdSession' : IdSession['value'], 'IdApplication' : '142', 'TypeAcces' : 'MaFiche', 'TypeApplication' : '0'}
    s.post('https://esaip.alcuin.com/OpDotNet/Eplug/FPC/Process/Annuaire/Parcours/Parcours.aspx?GObjet='+GObjet+'&IdObjet='+usrId+'&IdTypeObjet=26&intIdUtilisateur='+usrId+'&IdOnglet=178&IdAnnDos=6449 ', data=data)# Le post que le get précedant nous a dit d'effectuer
    IDeleve = '54250'
    notestab = s.get('https://esaip.alcuin.com/OpDotNet/Eplug/FPC/Process/Annuaire/Parcours/pDetailParcours.aspx?idProcess=31294&idUser='+IDeleve+'&idIns=439755&idProcessUC=-1&typeRef=module').text#Le get final qui nous retourne le tableau avec les notes, il fau modifier l'ID ICI
    notestabsoup = BeautifulSoup(notestab, "html.parser")# Préparation de la page avec beautiful soup
    notes = notestabsoup.find_all("tr", {"class": "DataGridItem"})# Recherche de toutes les lignes du tableau de notes
    for notes in notes: #Pour chaque lignes
        notes = notes.find_all("td", {"class": "DataGridColumn EncadrementPaveRL"})# Récupération de toutes les lignes qui correspondent à une matière (class=DataGridColumn EncadrementPaveRL)
        if len(notes) > 0:# Si la ligne correspond bien au critère de classe
            liste = ['']# Initialisation de la liste des valeurs pour chaque colonne
            for notes in notes:# Pour chaque colonne de la ligne
                liste.append(notes.text.strip())#On l'ajoute à la liste(suppression des espaces avant et après les valeurs pour que ce soit propre et que les valeurs vides le soient vraiment)
            if len(liste[5]) != 0:#Si il y a une note on l'ajoute à la BDD avec le nom de la matière.
                print('Dans la matière ',liste[1],' la note est',liste[5],' avec un coeff de ', liste[4])

    #Il reste à faire le beautiful soup
def retrieveMatiere(s):
    r = s.get('https://esaip.alcuin.com/OpDotNet/Context/context.jsx')  #Get user ID to show the right calendar
    usrId = re.search('\w+[0-9]', r.text).group(0)  #Regex to extract user ID
    #data = {'IdApplication': '190', 'TypeAcces': 'Utilisateur', 'url': '/EPlug/Agenda/Agenda.asp', 'session_IdCommunaute': '561', 'session_IdUser': usrId, 'session_IdGroupe': '786', 'session_IdLangue': '1'}
    #f = s.post("https://esaip.alcuin.com/commun/aspxtoasp.asp", data=data)  #Retrieve the calendar and create the necessary token
    #r = s.post("https://esaip.alcuin.com/EPlug/Agenda/Agenda.asp", data={"NumDat": 20220119, "DebHor": "08", "FinHor": "18", "ValGra": "60", "NomCal":"PRJ13230", "TypVis":"Vis-Jrs.xsl"}) #Extract a specific day
    s.get('https://esaip.alcuin.com/OpDotNet/Eplug/Annuaire/Accueil.aspx?IdApplication=142&TypeAcces=MaFiche&IdLien=6816') #Get obligatoir pour accéder au get suivant
    GObjet = s.get('https://esaip.alcuin.com/OpDotNet/Eplug/Annuaire/Navigation/Dossier/Dossier.aspx').text # Get pour que le serveur nous renvoie le GObjet qui change tous le temps
    GObjet = GObjet[GObjet.index('GObjet=')+len('GObjet='):GObjet.index('&IdObjet')] # Dans la réponse du Get précedant on extrait le code GObjet
    g = s.get('https://esaip.alcuin.com/OpDotNet/Noyau/Utils/LaunchAppli.aspx?IdApplication=142&TypeAcces=MaFiche&groupe=&TypeAppli=0&url=%2fOpDotNet%2fEplug%2fFPC%2fProcess%2fAnnuaire%2fParcours%2fParcours.aspx%3fGObjet%3d'+GObjet+'%26IdObjet%3d54268%26IdTypeObjet%3d26%26intIdUtilisateur%3d54268%26IdOnglet%3d178%26IdAnnDos%3d6449') # Get qui nous renvoie le post a réaliser (quand on clique sur l'onglet parcour)
    soup = BeautifulSoup(g.text, "html.parser")
    IdSession = soup.find(attrs={"name": "IdSession"} )
    data = {'dUser' : usrId, 'IdCommunity' : '561', 'Idgroupe' : '', 'groupe' : '', 'IdSession' : IdSession['value'], 'IdApplication' : '142', 'TypeAcces' : 'MaFiche', 'TypeApplication' : '0'}
    s.post('https://esaip.alcuin.com/OpDotNet/Eplug/FPC/Process/Annuaire/Parcours/Parcours.aspx?GObjet='+GObjet+'&IdObjet='+usrId+'&IdTypeObjet=26&intIdUtilisateur='+usrId+'&IdOnglet=178&IdAnnDos=6449 ', data=data)# Le post que le get précedant nous a dit d'effectuer
    notestab = s.get('https://esaip.alcuin.com/OpDotNet/Eplug/FPC/Process/Annuaire/Parcours/pDetailParcours.aspx?idProcess=31294&idUser='+usrId+'&idIns=439755&idProcessUC=-1&typeRef=module').text#Le get final qui nous retourne le tableau avec les notes, il fau modifier l'ID ICI
    notestabsoup = BeautifulSoup(notestab, "html.parser")# Préparation de la page avec beautiful soup
    tableau = notestabsoup.find_all("tr", {"class": "DataGridItem"})# Recherche de toutes les lignes du tableau de notes
    for ligne in tableau: #Pour chaque lignes
        lignematiere = ligne.find_all("td", {"class": "DataGridColumn EncadrementPaveRL"})# Récupération de toutes les lignes qui correspondent à une matière (class=DataGridColumn EncadrementPaveRL)
        if len(lignematiere) > 0:# Si la ligne correspond bien au critère de classe
            colval = ['']# Initialisation de la liste des valeurs pour chaque colonne
            for val in lignematiere:# Pour chaque colonne de la ligne
                colval.append(val.text.strip())#On l'ajoute à la liste(suppression des espaces avant et après les valeurs pour que ce soit propre et que les valeurs vides le soient vraiment)
            sql = 'SELECT * FROM Noms WHERE ID = "'+colval[1]+'"'
            cursor.execute(sql)# On check si l'ID est déjà dans la BDD, si on a rien en réponse alors on effectue la requête sinon on passe
            if len(cursor.fetchall()) != 1:
                try:
                    sql = "INSERT INTO Matiere (Nom, Coeff ) VALUES (%s, %s)"
                    val = (colval[1], colval[4].replace(",", "."))
                    cursor.execute(sql, val)
                    mydb.commit()
                    print('Ajout de la matière',colval[1],' qui a un Coeff de ',colval[4])
                except:
                    pass
                

def IDtoNom(s):
    for IDeleve in range(1700,60000):
        Nom = ""
        Prenom = ""
        sql = "SELECT * FROM Noms WHERE ID = '"+str(IDeleve)+"'"
        cursor.execute(sql)# On check si l'ID est déjà dans la BDD, si on a rien en réponse alors on effectue la requête sinon on passe
        if len(cursor.fetchall()) != 1:
            s.get('https://esaip.alcuin.com/OpDotNet/Eplug/Annuaire/Accueil.aspx?IdApplication=142&TypeAcces=MaFiche&IdLien=6816') #Get obligatoir pour accéder au get suivant
            GObjet = s.get('https://esaip.alcuin.com/OpDotNet/Eplug/Annuaire/Navigation/Dossier/Dossier.aspx').text # Get pour que le serveur nous renvoie le GObjet qui change tous le temps
            GObjet = GObjet[GObjet.index('GObjet=')+len('GObjet='):GObjet.index('&IdObjet')] # Dans la réponse du Get précedant on extrait le code GObjet
            s.get('https://esaip.alcuin.com/OpDotNet/site/Scripts/plugins/RequireJS/require.js') #Get obligatoir pour accéder au get suivant
            NomPrenom = s.get('https://esaip.alcuin.com/OpDotNet/Eplug/Annuaire/Navigation/Dossier/esaip_dossieretudiant.opx?GObjet='+GObjet+'&IdObjet='+str(IDeleve)+'&IdTypeObjet=26&intIdUtilisateur='+str(IDeleve)+'&IdOnglet=245&IdAnnDos=6449&1onglet=1').text # Get qui nous renvoie le post a réaliser (quand on clique sur l'onglet parcour)
            NomPrenom = BeautifulSoup(NomPrenom, "html.parser")
            try:
                for Nom in  NomPrenom.find('div',{'id' : 'NOM'}).find('div', attrs={"class":'form_fieldValue'}):
                    Nom = Nom.strip()
                for Prenom in  NomPrenom.find('div',{'id' : 'PRE'}).find('div', attrs={"class":'form_fieldValue'}):
                    Prenom = Prenom.strip()
                try:
                    sql = 'INSERT INTO Noms (ID, Nom, prenom ) VALUES (%s, %s, %s)'
                    val = (IDeleve, Nom, Prenom)
                    cursor.execute(sql, val)
                    mydb.commit()
                    print('Ajout de ',Prenom,' ',Nom,' qui a l\'ID ',IDeleve)
                except:
                    pass
            except:
                print ('L\'ID ',IDeleve,'n\'a pas d\'élève')
        else:
            print(cursor.fetchall())
            print('Déjà présent')
        


def usage():
    print("Usage: main.py [-h] [-o output] days")
    
if __name__ == "__main__":
    main(sys.argv[1:])
mydb.close()
print("[*] Déconnecté de la BDD")
