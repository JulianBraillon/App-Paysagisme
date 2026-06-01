from db.database import connexion_db

def ajouter_devis(client_id, description, montant, statut):
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO devis(client_id, description, montant, statut)
    VALUES (?, ?, ?, ?)
    """, (client_id, description, montant, statut))
    conn.commit()
    conn.close()

def afficher_devis():
    """Tous les devis (vue admin)"""
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT devis.id,
           clients.nom || ' ' || clients.prenom,
           devis.description,
           devis.montant,
           devis.statut,
           devis.date_creation
    FROM devis
    JOIN clients ON devis.client_id = clients.id
    ORDER BY devis.id DESC
    """)
    data = cur.fetchall()
    conn.close()
    return data

def afficher_devis_client(client_id):
    """Devis d'un client spécifique"""
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT devis.id,
           clients.nom || ' ' || clients.prenom,
           devis.description,
           devis.montant,
           devis.statut,
           devis.date_creation
    FROM devis
    JOIN clients ON devis.client_id = clients.id
    WHERE devis.client_id = ?
    ORDER BY devis.id DESC
    """, (client_id,))
    data = cur.fetchall()
    conn.close()
    return data

def changer_statut(devis_id, nouveau_statut):
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("UPDATE devis SET statut = ? WHERE id = ?", (nouveau_statut, devis_id))
    conn.commit()
    conn.close()

def supprimer_devis(devis_id):
    conn = connexion_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM devis WHERE id = ?", (devis_id,))
    conn.commit()
    conn.close()

def modifier_devis(devis_id, description, montant):
    """Modifier un devis existant (seulement si en attente)"""
    conn = connexion_db()
    cur = conn.cursor()
    
    cur.execute("SELECT statut FROM devis WHERE id=?", (devis_id,))
    result = cur.fetchone()
    
    if result and result[0] == "En attente":
        cur.execute("""
        UPDATE devis 
        SET description=?, montant=?
        WHERE id=?
        """, (description, montant, devis_id))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def supprimer_devis_client(devis_id, client_id):
    """Supprimer un devis (seulement si en attente et appartient au client)"""
    conn = connexion_db()
    cur = conn.cursor()
    
    cur.execute("""
    SELECT id FROM devis 
    WHERE id=? AND client_id=? AND statut='En attente'
    """, (devis_id, client_id))
    
    if cur.fetchone():
        cur.execute("DELETE FROM devis WHERE id=?", (devis_id,))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False