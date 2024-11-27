# -- coding: utf-8 --
"""
@authors:   SOALEHY Salahouddine Samir
            ETIEN Nissi Christ Emmanuel
            EL HAMMOUTI Mohammed
            KHOUDI Oualid
"""

import tkinter as tk
import sqlite3
from tkinter import Frame, ttk, messagebox
import xml.etree.ElementTree as ET

def setup_database():
    
    # Connexion à la base de données SQLite
    conn = sqlite3.connect("rh_database.db")
    cursor = conn.cursor()
    
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        poste TEXT NOT NULL,
        salaire REAL NOT NULL
    )
    """)
        
    conn.commit()
    conn.close()

#
LISTE_POSTES = ["Directeur", "Chef de projet", "Technicien", "Développeur informatique", "Analyste de données", "Sécurité informatique"]

def ajouter_employe():
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    poste = combobox_poste.get()  
    salaire = entry_salaire.get()
    
    # Vérifie que tous les champs sont remplis
    if not (nom and prenom and poste and salaire):
        messagebox.showerror("Erreur", "Tous les champs sont requis.")
        return
    
    try:
        conn = sqlite3.connect("rh_database.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO employes (nom, prenom, poste, salaire)
        VALUES (?, ?, ?, ?)
        """, (nom, prenom, poste, float(salaire)))
        conn.commit()
        conn.close()
        afficher_employes()
        messagebox.showinfo("Succès", "Employé ajouté avec succès.")
        vider_champs()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout : {e}")

def afficher_employes():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("rh_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employes")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

def selectionner_employe(event):
    try:
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, "values")
        ouvrir_fenetre_employe(values)
    except IndexError:
        pass

def ouvrir_fenetre_employe(employe):
    fenetre_employe = tk.Toplevel(root)
    fenetre_employe.title("Détails de l'employé")
    fenetre_employe.geometry("400x300")

    # Champ Nom
    tk.Label(fenetre_employe, text="Nom").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nom_fenetre = ttk.Entry(fenetre_employe)
    entry_nom_fenetre.grid(row=0, column=1, padx=5, pady=5)
    entry_nom_fenetre.insert(0, employe[1])

    # Champ Prénom
    tk.Label(fenetre_employe, text="Prénom").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_prenom_fenetre = ttk.Entry(fenetre_employe)
    entry_prenom_fenetre.grid(row=1, column=1, padx=5, pady=5)
    entry_prenom_fenetre.insert(0, employe[2])

    # Menu déroulant pour le poste
    LISTE_POSTES = ["Directeur", "Chef de projet", "Technicien", "Développeur informatique", "Analyste de données", "Sécurité informatique"]
    tk.Label(fenetre_employe, text="Poste").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    combobox_poste = ttk.Combobox(fenetre_employe, values=LISTE_POSTES, state="readonly")
    combobox_poste.grid(row=2, column=1, padx=5, pady=5)
    combobox_poste.set(employe[3]) 

    # Champ Salaire
    tk.Label(fenetre_employe, text="Salaire").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_salaire_fenetre = ttk.Entry(fenetre_employe)
    entry_salaire_fenetre.grid(row=3, column=1, padx=5, pady=5)
    entry_salaire_fenetre.insert(0, employe[4])

    # Bouton Modifier
    def modifier_employe():
        nom = entry_nom_fenetre.get()
        prenom = entry_prenom_fenetre.get()
        poste = combobox_poste.get()
        salaire = entry_salaire_fenetre.get()

        if not (nom and prenom and poste and salaire):
            messagebox.showerror("Erreur", "Tous les champs sont requis.")
            return

        try:
            conn = sqlite3.connect("rh_database.db")
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE employes
            SET nom = ?, prenom = ?, poste = ?, salaire = ?
            WHERE id = ?
            """, (nom, prenom, poste, float(salaire), employe[0]))
            conn.commit()
            conn.close()
            afficher_employes()
            messagebox.showinfo("Succès", "Employé modifié avec succès.")
            fenetre_employe.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification : {e}")

    # Bouton Supprimer
    def supprimer_employe():
        try:
            conn = sqlite3.connect("rh_database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employes WHERE id = ?", (employe[0],))
            conn.commit()
            conn.close()
            afficher_employes()
            messagebox.showinfo("Succès", "Employé supprimé avec succès.")
            fenetre_employe.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")

    ttk.Button(fenetre_employe, text="Modifier", command=modifier_employe).grid(row=4, column=0, pady=20, padx=5)
    ttk.Button(fenetre_employe, text="Supprimer", command=supprimer_employe).grid(row=4, column=1, pady=20, padx=5)

def vider_champs():
    entry_nom.delete(0, tk.END)
    entry_prenom.delete(0, tk.END)
    combobox_poste.set("Sélectionnez un poste") 
    entry_salaire.delete(0, tk.END)



# Partie XML_________________________________


def exporter_employes_xml():
    try:
        # Connexion à la base de données SQLite
        conn = sqlite3.connect("rh_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employes")
        employes = cursor.fetchall()
        conn.close()

        if not employes:
            messagebox.showwarning("Aucun employé", "Aucun employé à exporter.")
            return

        # Créer l'élément racine du XML
        root = ET.Element("employes")

        # Ajouter des employés à l'élément racine
        for employe in employes:
            employe_element = ET.SubElement(root, "employe")
            ET.SubElement(employe_element, "id").text = str(employe[0])
            ET.SubElement(employe_element, "nom").text = employe[1]
            ET.SubElement(employe_element, "prenom").text = employe[2]
            ET.SubElement(employe_element, "poste").text = employe[3]
            ET.SubElement(employe_element, "salaire").text = str(employe[4])

        # Créer l'arbre XML
        tree = ET.ElementTree(root)

        # Enregistrer le fichier XML avec une indentation
        with open("employes.xml", "wb") as fichier:
            tree.write(fichier, encoding="utf-8", xml_declaration=True)

        # Optionnel : Améliorer l'indentation pour rendre le XML plus lisible
        from xml.dom import minidom
        with open("employes.xml", "r", encoding="utf-8") as fichier:
            xml_str = fichier.read()
            reparsed = minidom.parseString(xml_str)
            with open("employes.xml", "w", encoding="utf-8") as fichier:
                fichier.write(reparsed.toprettyxml(indent="  "))  # Indentation de 2 espaces

        messagebox.showinfo("Succès", "Les employés ont été exportés vers employes.xml.")
        print("Employés exportés avec succès.")  # Débogage

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {e}")


# Fonction pour mettre à jour un employé dans le fichier XML
def mettre_a_jour_employe_xml(id_employe, nom, prenom, poste, salaire):
    try:
        tree = ET.parse("employes.xml")
        root = tree.getroot()

        employe_a_mettre_a_jour = None
        for employe in root.findall("employe"):
            if employe.find("id").text == str(id_employe):
                employe_a_mettre_a_jour = employe
                break

        if employe_a_mettre_a_jour is not None:
            employe_a_mettre_a_jour.find("nom").text = nom
            employe_a_mettre_a_jour.find("prenom").text = prenom
            employe_a_mettre_a_jour.find("poste").text = poste
            employe_a_mettre_a_jour.find("salaire").text = str(salaire)
            tree.write("employes.xml")
            messagebox.showinfo("Succès", f"L'employé avec l'ID {id_employe} a été mis à jour dans le fichier XML.")
        else:
            messagebox.showwarning("Non trouvé", f"Aucun employé avec l'ID {id_employe} trouvé dans le fichier XML.")
    except FileNotFoundError:
        messagebox.showerror("Erreur", "Le fichier employes.xml n'existe pas. Veuillez d'abord l'exporter.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la mise à jour dans le fichier XML : {e}")

# Fonction pour afficher la fenêtre de mise à jour
def mettre_a_jour_employe_xml_popup():
    def mettre_a_jour():
        try:
            id_employe = int(entry_id_employe.get())
            nom = entry_nom.get()
            prenom = entry_prenom.get()
            poste = combobox_poste.get()
            salaire = float(entry_salaire.get())

            if not (nom and prenom and poste and salaire):
                messagebox.showerror("Erreur", "Tous les champs sont requis.")
                return

            mettre_a_jour_employe_xml(id_employe, nom, prenom, poste, salaire)
            fenetre_popup.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des informations valides.")

    fenetre_popup = tk.Toplevel(root)
    fenetre_popup.title("Mettre à jour un employé XML")
    fenetre_popup.geometry("350x300")

    tk.Label(fenetre_popup, text="ID de l'employé :", font=("Helvetica", 10)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_id_employe = ttk.Entry(fenetre_popup)
    entry_id_employe.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(fenetre_popup, text="Nom :", font=("Helvetica", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_nom = ttk.Entry(fenetre_popup)
    entry_nom.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(fenetre_popup, text="Prénom :", font=("Helvetica", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_prenom = ttk.Entry(fenetre_popup)
    entry_prenom.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(fenetre_popup, text="Poste :", font=("Helvetica", 10)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
    combobox_poste = ttk.Combobox(fenetre_popup, values=LISTE_POSTES, state="readonly")
    combobox_poste.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(fenetre_popup, text="Salaire :", font=("Helvetica", 10)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_salaire = ttk.Entry(fenetre_popup)
    entry_salaire.grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(fenetre_popup, text="Mettre à jour", command=mettre_a_jour).grid(row=5, column=1, pady=20, padx=5)


def supprimer_employe_xml(id_employe):
    try:
        # Charger le fichier XML
        tree = ET.parse("employes.xml")
        root = tree.getroot()

        # Rechercher l'employé par son ID et supprimer
        employe_a_supprimer = None
        for employe in root.findall("employe"):
            if employe.find("id").text == str(id_employe):
                employe_a_supprimer = employe
                break

        # Si l'employé est trouvé, le supprimer
        if employe_a_supprimer is not None:
            root.remove(employe_a_supprimer)  # Suppression de l'employé
            tree.write("employes.xml")  # Sauvegarde du fichier XML modifié
            messagebox.showinfo("Succès", f"L'employé avec l'ID {id_employe} a été supprimé du fichier XML.")
        else:
            messagebox.showwarning("Non trouvé", f"Aucun employé avec l'ID {id_employe} trouvé dans le fichier XML.")

    except FileNotFoundError:
        messagebox.showerror("Erreur", "Le fichier employes.xml n'existe pas. Veuillez d'abord l'exporter.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")


def supprimer_employe_xml_popup():
    # Fenêtre popup pour demander l'ID de l'employé à supprimer
    def supprimer():
        try:
            id_employe = int(entry_id_employe.get())
            supprimer_employe_xml(id_employe)
            fenetre_popup.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un ID valide.")

    fenetre_popup = tk.Toplevel(root)
    fenetre_popup.title("Supprimer un employé XML")
    fenetre_popup.geometry("300x150")

    tk.Label(fenetre_popup, text="ID de l'employé à supprimer :", font=("Helvetica", 10)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_id_employe = ttk.Entry(fenetre_popup)
    entry_id_employe.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(fenetre_popup, text="Supprimer", command=supprimer).grid(row=1, column=1, padx=10, pady=10)

#________________________________________________________________________________________________________________



setup_database()
root = tk.Tk()
root.title("Gestion des Ressources Humaines")
root.geometry("700x500")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
style.map("Treeview", background=[("selected", "blue")])

frame_form = tk.LabelFrame(root, text="Formulaire Employé", padx=10, pady=10)
frame_form.pack(fill="x", padx=10, pady=10)

tk.Label(frame_form, text="Nom").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_nom = ttk.Entry(frame_form)
entry_nom.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Prénom").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_prenom = ttk.Entry(frame_form)
entry_prenom.grid(row=1, column=1, padx=5, pady=5)

LISTE_POSTES = ["Directeur", "Chef de projet", "Technicien", "Développeur informatique", "Analyste de données", "Sécurité informatique"]
tk.Label(frame_form, text="Poste").grid(row=2, column=0, padx=5, pady=5, sticky="w")
combobox_poste = ttk.Combobox(frame_form, values=LISTE_POSTES, state="readonly")
combobox_poste.grid(row=2, column=1, padx=5, pady=5)
combobox_poste.set("Sélectionnez un poste")

tk.Label(frame_form, text="Salaire").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_salaire = ttk.Entry(frame_form)
entry_salaire.grid(row=3, column=1, padx=5, pady=5)




button_frame = Frame(root)
button_frame.pack(pady=20)

btn_ajouter = ttk.Button(button_frame, text="Ajouter Employé", command=ajouter_employe)
btn_ajouter.pack(side="left", padx=10)

btn_exporter = ttk.Button(button_frame, text="Exporter vers XML", command=exporter_employes_xml)
btn_exporter.pack(side="left", padx=10)

btn_supprimer = ttk.Button(button_frame, text="Supprimer Employé -> XML", command=supprimer_employe_xml_popup)
btn_supprimer.pack(side="left", padx=10)

btn_modifier = ttk.Button(button_frame, text="Modifier Employé -> XML", command=mettre_a_jour_employe_xml_popup)
btn_modifier.pack(side="left", padx=10)



tree = ttk.Treeview(root, columns=("ID", "Nom", "Prénom", "Poste", "Salaire"), show="headings")

tree.heading("ID", text="ID")
tree.heading("Nom", text="Nom")
tree.heading("Prénom", text="Prénom")
tree.heading("Poste", text="Poste")
tree.heading("Salaire", text="Salaire")
tree.pack(fill="both", expand=True, padx=10, pady=10)
tree.bind("<<TreeviewSelect>>", selectionner_employe)

afficher_employes()

root.mainloop()