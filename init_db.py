import hashlib
import sqlite3
import os
from db.database import connexion_db

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def init_database():
    conn = connexion_db()
    cur = conn.cursor()

    # TABLE CLIENTS avec téléphone UNIQUE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        nom           TEXT    NOT NULL,
        prenom        TEXT,
        telephone     TEXT    UNIQUE,
        email         TEXT    UNIQUE NOT NULL,
        adresse       TEXT,
        role          TEXT    DEFAULT 'client',
        mot_de_passe  TEXT    NOT NULL
    )
    """)

    # TABLE DEVIS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS devis (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id     INTEGER NOT NULL,
        description   TEXT,
        montant       REAL,
        statut        TEXT    DEFAULT 'En attente',
        date_creation TEXT    DEFAULT (date('now')),
        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
    )
    """)

    # ADMIN
    cur.execute("""
    INSERT OR IGNORE INTO clients(id, nom, prenom, telephone, email, adresse, role, mot_de_passe)
    VALUES (1, 'Admin', 'System', '0000000000', 'admin@paysagisme.fr', 'Lyon', 'admin', ?)
    """, (hash_pwd("admin1234"),))

    # CLIENTS DE TEST
    existing = cur.execute("SELECT COUNT(*) FROM clients WHERE role = 'client'").fetchone()[0]
    if existing == 0:
        clients = [
            ("Dupont",    "Jean",      "0612345601", "jean.dupont@mail.fr",      "12 rue des Lilas, Lyon",          "client", hash_pwd("jean1234")),
            ("Martin",    "Claire",    "0612345602", "claire.martin@mail.fr",    "8 avenue Foch, Paris",            "client", hash_pwd("claire1234")),
            ("Bernard",   "Lucas",     "0612345603", "lucas.bernard@mail.fr",    "34 bd Michelet, Marseille",       "client", hash_pwd("lucas1234")),
            ("Petit",     "Emma",      "0612345604", "emma.petit@mail.fr",       "5 rue Nationale, Lille",          "client", hash_pwd("emma1234")),
            ("Robert",    "Hugo",      "0612345605", "hugo.robert@mail.fr",      "18 promenade des Anglais, Nice",  "client", hash_pwd("hugo1234")),
            ("Leroy",     "Mathilde",  "0612345606", "mathilde.leroy@mail.fr",   "23 rue Carnot, Bordeaux",         "client", hash_pwd("mathilde1234")),
            ("Moreau",    "Thomas",    "0612345607", "thomas.moreau@mail.fr",    "7 rue de la Paix, Strasbourg",    "client", hash_pwd("thomas1234")),
            ("Simon",     "Julie",     "0612345608", "julie.simon@mail.fr",      "56 avenue Jean Jaurès, Toulouse", "client", hash_pwd("julie1234")),
            ("Laurent",   "Antoine",   "0612345609", "antoine.laurent@mail.fr",  "91 rue de la République, Nantes", "client", hash_pwd("antoine1234")),
            ("Fontaine",  "Camille",   "0612345610", "camille.fontaine@mail.fr", "14 cours Mirabeau, Aix-en-Prov.", "client", hash_pwd("camille1234")),
        ]
        cur.executemany("""
        INSERT INTO clients(nom, prenom, telephone, email, adresse, role, mot_de_passe)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, clients)

    # DEVIS DE TEST
    existing_d = cur.execute("SELECT COUNT(*) FROM devis").fetchone()[0]
    if existing_d == 0:
        devis = [
            (2, "Taille haie + pelouse avant",        120.00, "En attente", "2025-03-05"),
            (2, "Création jardin méditerranéen",      2800.00, "Accepté",   "2025-03-18"),
            (3, "Aménagement terrasse bois",          1400.00, "En attente", "2025-03-10"),
            (3, "Pose gazon synthétique",              950.00, "Refusé",     "2025-03-22"),
            (4, "Élagage arbres fruitiers",            340.00, "Accepté",   "2025-02-14"),
            (4, "Création allée gravillons",           620.00, "En attente", "2025-04-08"),
            (5, "Pose clôture bois 40m",               800.00, "Refusé",    "2025-01-28"),
            (6, "Aménagement terrasse pierre",        2200.00, "En attente", "2025-05-12"),
            (7, "Jardin japonais — conception",       3500.00, "Accepté",   "2025-03-01"),
            (8, "Réfection pelouse 200m²",             540.00, "En attente", "2025-05-05"),
            (9, "Pergola végétalisée",                1850.00, "Accepté",   "2025-02-20"),
            (10, "Taille palmiers + nettoyage",        390.00, "Refusé",    "2025-04-11"),
        ]
        cur.executemany("""
        INSERT INTO devis(client_id, description, montant, statut, date_creation)
        VALUES (?, ?, ?, ?, ?)
        """, devis)

    conn.commit()
    conn.close()
    print("✅ Base initialisée — téléphone UNIQUE, clé étrangère CASCADE")

if __name__ == "__main__":
    init_database()