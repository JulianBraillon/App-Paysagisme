import hashlib
from db.database import connexion_db

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def login_client(email: str, mot_de_passe: str):
    """Retourne la ligne client si email + mdp corrects, sinon None."""
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM clients WHERE email = ? AND mot_de_passe = ?",
        (email, hash_pwd(mot_de_passe))
    )
    user = cur.fetchone()
    conn.close()
    return user

def email_existe(email: str) -> bool:
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM clients WHERE email = ?", (email,))
    r = cur.fetchone()
    conn.close()
    return r is not None

def telephone_existe(telephone: str, exclude_id=None) -> bool:
    """Vérifie si un numéro de téléphone existe déjà"""
    conn = connexion_db()
    cur = conn.cursor()
    if exclude_id:
        cur.execute("SELECT id FROM clients WHERE telephone = ? AND id != ?", (telephone, exclude_id))
    else:
        cur.execute("SELECT id FROM clients WHERE telephone = ?", (telephone,))
    r = cur.fetchone()
    conn.close()
    return r is not None

def inscrire_client(nom, prenom, telephone, email, adresse, mot_de_passe):
    """Inscription publique — rôle client uniquement."""
    conn = connexion_db()
    cur = conn.cursor()
    
    # Vérifier si le téléphone existe déjà
    if telephone and telephone.strip():
        if telephone_existe(telephone):
            conn.close()
            raise ValueError("Ce numéro de téléphone est déjà utilisé")
    
    cur.execute("""
    INSERT INTO clients(nom, prenom, telephone, email, adresse, role, mot_de_passe)
    VALUES (?, ?, ?, ?, ?, 'client', ?)
    """, (nom, prenom, telephone if telephone else None, email, adresse, hash_pwd(mot_de_passe)))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def afficher_clients():
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, nom, prenom, telephone, email, adresse, role
    FROM clients ORDER BY id
    """)
    data = cur.fetchall()
    conn.close()
    return data

def ajouter_client(nom, prenom, telephone, email, adresse, role="client", mot_de_passe="changeme"):
    conn = connexion_db()
    cur = conn.cursor()
    
    # Vérifier si le téléphone existe déjà
    if telephone and telephone.strip():
        if telephone_existe(telephone):
            conn.close()
            raise ValueError("Ce numéro de téléphone est déjà utilisé")
    
    cur.execute("""
    INSERT INTO clients(nom, prenom, telephone, email, adresse, role, mot_de_passe)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nom, prenom, telephone if telephone else None, email, adresse, role, hash_pwd(mot_de_passe)))
    conn.commit()
    conn.close()

def supprimer_client(id_client):
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM devis WHERE client_id = ?", (id_client,))
    cur.execute("DELETE FROM clients WHERE id = ?", (id_client,))
    conn.commit()
    conn.close()

def modifier_profil(client_id, nom, prenom, telephone, email, adresse, mot_de_passe=None):
    """Modifier le profil client"""
    conn = connexion_db()
    cur = conn.cursor()
    
    # Vérifier si le téléphone existe déjà pour un autre client
    if telephone and telephone.strip():
        if telephone_existe(telephone, client_id):
            conn.close()
            raise ValueError("Ce numéro de téléphone est déjà utilisé par un autre client")
    
    # Vérifier si l'email existe déjà pour un autre client
    cur.execute("SELECT id FROM clients WHERE email = ? AND id != ?", (email, client_id))
    if cur.fetchone():
        conn.close()
        raise ValueError("Cet email est déjà utilisé par un autre client")
    
    if mot_de_passe and mot_de_passe.strip():
        cur.execute("""
        UPDATE clients 
        SET nom=?, prenom=?, telephone=?, email=?, adresse=?, mot_de_passe=?
        WHERE id=?
        """, (nom, prenom, telephone if telephone else None, email, adresse, hash_pwd(mot_de_passe), client_id))
    else:
        cur.execute("""
        UPDATE clients 
        SET nom=?, prenom=?, telephone=?, email=?, adresse=?
        WHERE id=?
        """, (nom, prenom, telephone if telephone else None, email, adresse, client_id))
    
    conn.commit()
    conn.close()

def supprimer_compte_client(client_id):
    """Supprimer un compte client et tous ses devis"""
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id = ? AND role = 'client'", (client_id,))
    conn.commit()
    conn.close()

def get_client_info(client_id):
    """Récupérer les informations d'un client"""
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, nom, prenom, telephone, email, adresse, role
    FROM clients WHERE id=?
    """, (client_id,))
    data = cur.fetchone()
    conn.close()
    return data