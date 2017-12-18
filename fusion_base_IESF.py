#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-
"""
Synchronisation de la base des anciens avec celle de l'IESF pour soumission
des nouveaux anciens à l'IESF

https://repertoire.iesf.fr/import-diplomes

Script en UTF-8 mais doit être lancé dans un terminal ISO-8859-1

"""
from __future__ import print_function
import sys
import argparse
import datetime
import csv


def importBaseIESF(bIESF):
    """
    import de la base actuelle IESF afin d'y inclure les modifications ou d'ajouter les nouveaux diplômés

    actuellement il manque souvent la date de naissance
    le status décès doit être ajouté si concerné

    format CSV :
    N°IESF;Nom d'usage;Nom de famille;Prénom;Date de naissance (JJ/MM/AAAA);Décédé;N°école ou UAI;Promotion;Code SISE;Formation;Titre thèse;Numéro ingénieur association

    ancien format CSV (avant 2017) :
    NEW;N° association;N° école associée ou Code UAI pour université;Nom d'usage (ex nom de famille);Nom de famille (ex nom de JF);Prénom;Date naissance;Millésime promotion;N° ingénieur asso;N° ingénieur IESF;Mot de passe;Statut;Code SISE pour université;Titre Thèse pour université
    
    """
    out = {}
    out_ignore = []
    lectureCSV = csv.reader(bIESF, delimiter=';')

    row = lectureCSV # consomation de la première ligne 
    
    for row in lectureCSV:
        if out.get(row[11], False):
            print ("Erreur : doublon ", row[11])
            out_ignore.append(row[0])
        else:
            out[row[11]] = row
    print (out_ignore)
    return (out, out_ignore)

def importBaseAnciens(bAnciens, BaseAFusionner, exclusion):
    """
    import de la base existante dans un dictionnaire indéxé par l'identifiant unique de l'ancien
    (numéro d'ancien coté école)

    Format actuel (2015)
    "no_personne";"date_crea";"date_modif";"modifie_par";"sexe";"classe";"login";"password";"statut";"dernier_login";"si_npai";"nom";"nom_jeune_fille";"prenom";"vit_avec";"promo";"coache_par";"type";"type_str";"situation";"si_major";"date_naissance";"lieu_naissance";"si_deces";"date_deces";"date_retraite";"perso_parent";"perso_rue_1";"perso_rue_2";"perso_ville";"perso_cp";"perso_pays";"perso_region";"perso_tel";"perso_fax";"perso_gsm";"perso_email";"perso_url";"perso_blog";"perso_skype";"perso_date_modif";"perso_modifie_par";"pro_organisation";"organisation_desc";"organisation_naf";"pro_fonction";"pro_fonction_desc";"pro_secteur";"pro_rue_1";"pro_rue_2";"pro_ville";"pro_cp";"pro_pays";"pro_region";"pro_tel";"pro_fax";"pro_gsm";"pro_email";"pro_date_modif";"pro_modifie_par";"pro_url";"pro_desc";"pro_situation";"pro_position";"ben_organisation";"ben_fonction_desc";"ben_activite";"ben_rue_1";"ben_rue_2";"ben_ville";"ben_cp";"ben_pays";"ben_region";"ben_tel";"ben_fax";"ben_email";"ben_desc";"parent_civilite";"parent_nom";"parent_rue_1";"parent_rue_2";"parent_ville";"parent_cp";"parent_pays";"parent_tel";"parent_email";"abo_liste_promo";"abo_revue";"email4life";"email4life_addr";"diplomes";"nationalite";"commentaires";"pro_commentaires";"profil_type";"profil_cible";"lang";"mailing_coord";"contact_coord";"si_portailrh";"prelev_auto";"rib";"date_modif_bouge";"est_delegue_promo";"est_delegue_organisation";"est_delegue_region";"--FIN DE LIGNE--"
    
    """
    baseFinale = []

    lectureCSV = csv.reader(bAnciens, delimiter=';')

    row = next(lectureCSV) # consomation de la première ligne 
    # Création des index
    index_enreg = {}
    index_champ = 0
    for enregistrement in row:
        index_enreg[enregistrement] = index_champ
        index_champ += 1

    # parcours de la base
    for row in lectureCSV:
        numAncien = row[index_enreg['no_personne']]
        promo = row[index_enreg['promo']]
        annee = promo
        dateNaiss = row[index_enreg['date_naissance']]
        if promo.endswith("-MASTERS"):
            annee = promo.split("-")[0]

        if numAncien in exclusion or row[index_enreg['classe']] in ["Elève", "Partenaire", "Public"] or promo == "0000" or int(annee) >= datetime.datetime.now().year:
            print("ignore %s" % numAncien, file=sys.stderr)
        else:
    
            if dateNaiss == "00/00/0000":
                dateNaiss = ""
    
            prenom = row[index_enreg['prenom']]
            if row[index_enreg['nom_jeune_fille']]:
                nom = row[index_enreg['nom_jeune_fille']]
                nomUsage = row[index_enreg['nom']]
            else:
                nom = ""
                nomUsage = row[index_enreg['nom']]


    
            if row[index_enreg['classe']] not in ["Ancien", "Membre du CA", "Permanent", "Administrateur informatique"]:
                print("A vérifier=%s (%s : %s %s)" % (numAncien, row[index_enreg['classe']], nom, prenom), file=sys.stderr)
                continue

            siDeces = row[index_enreg['si_deces']]
            if siDeces == "oui":
                print ("Décédé : %s %s %s" % (nomUsage, prenom, dateNaiss), file=sys.stderr)
            else:
                siDeces = ""

            if numAncien in BaseAFusionner: # == .has_key(numAncien):
                if dateNaiss and BaseAFusionner[numAncien][4] == "":
                    BaseAFusionner[numAncien][4] = dateNaiss
                if promo.endswith("-MASTERS"):
                    BaseAFusionner[numAncien][7] = annee
                    BaseAFusionner[numAncien][8] = "Master en Sciences et Technologies, mention Informatique (code RNCP: 24680)"
                    BaseAFusionner[numAncien][9] = "MS"
                elif int(annee) < 2010:
                    BaseAFusionner[numAncien][7] = annee
                    BaseAFusionner[numAncien][8] = "Expert en ingénierie informatique (code RNCP: 2164)"
                    BaseAFusionner[numAncien][9] = "MS"
                else:
                    BaseAFusionner[numAncien][8] = "6000686"
                baseFinale.append(BaseAFusionner[numAncien])
            else:
                codeSISE = ""
                numEcole = 410
                formation = "ID"
                # ID, MS, DS
                if promo.endswith("-MASTERS"):
                    promo = annee
                    formation = "MS"
                    codeSISE = "Master en Sciences et Technologies, mention Informatique (code RNCP: 24680)" 
                elif int(annee) < 2010:
                    promo = annee
                    formation = "MS"
                    codeSISE = "Expert en ingénierie informatique (code RNCP: 2164)"
                else:
                    codeSISE = "6000686"
                titreThese = ""
   
                baseFinale.append(["", nomUsage, nom, prenom, dateNaiss, siDeces, numEcole, promo, codeSISE, formation, titreThese, numAncien])
    return baseFinale




def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "bIESF", default="A235.csv",
        metavar="BaseIESF", type=argparse.FileType("r"),
        help="Base CSV des anciens enregistrés dans le répertoire IESF")

    parser.add_argument(
        "bAnciens", default="annuaire.csv",
        metavar="BaseAnciens", type=argparse.FileType("r"),
        help="Base CSV des diplômés de l'école")

    parser.add_argument(
        "bResultat", nargs="?", default="-",
        metavar="Resultat", type=argparse.FileType("w"),
        help="Fichier résultat à soumettre à l'IESF")

    args = parser.parse_args()

    exclusion = ["10001", "10002",
           # Numéro des anciens ayant demandé à ne pas y figurer
           '12705'
    ]

    baseFusionnee, baseIgnoree = importBaseIESF(args.bIESF)
    baseFinale = importBaseAnciens(args.bAnciens, baseFusionnee, exclusion)

    writer = csv.writer(args.bResultat, delimiter=';')
    writer.writerows(baseFinale)

#    file_ignore = open('ignorer.txt', 'w')
#    for ignore_elt in baseIgnoree:
#        file_ignore.write(ignore_elt + "\n")
#    file_ignore.close()

if __name__ == "__main__":
    main()


##
# Futur : si passage en UTF-8
##
#class UTF8Recoder:
#    """
#    Iterator that reads an encoded stream and reencodes the input to UTF-8
#    """
#    def __init__(self, f, encoding):
#       self.reader = codecs.getreader(encoding)(f)
#
#    def __iter__(self):
#       return self
#
#    def next(self):
#       return self.reader.next().encode("utf-8")
#
#class UnicodeReader:
#    """
#    A CSV reader which will iterate over lines in the CSV file "f",
#    which is encoded in the given encoding.
#    """
#
#    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
#        f = UTF8Recoder(f, encoding)
#        self.reader = csv.reader(f, dialect=dialect, **kwds)
#
#    def next(self):
#        row = self.reader.next()
#        return [unicode(s, "utf-8") for s in row]
#
#    def __iter__(self):
#        return self
#
#class UnicodeWriter:
#    """
#    A CSV writer which will write rows to CSV file "f",
#    which is encoded in the given encoding.
#    """
#
#    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
#        # Redirect output to a queue
#        self.queue = cStringIO.StringIO()
#        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
#        self.stream = f
#        self.encoder = codecs.getincrementalencoder(encoding)()
#
#    def writerow(self, row):
#        self.writer.writerow([s.encode("utf-8") for s in row])
#        # Fetch UTF-8 output from the queue ...
#        data = self.queue.getvalue()
#        data = data.decode("utf-8")
#        # ... and reencode it into the target encoding
#        data = self.encoder.encode(data)
#        # write to the target stream
#        self.stream.write(data)
#        # empty queue
#        self.queue.truncate(0)
#
#    def writerows(self, rows):
#        for row in rows:
#            self.writerow(row)
