import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from models.client import (login_client, afficher_clients, ajouter_client,
                            supprimer_client, inscrire_client, email_existe,
                            telephone_existe, modifier_profil, supprimer_compte_client,
                            get_client_info)
from models.devis import (ajouter_devis, afficher_devis, afficher_devis_client,
                            changer_statut, supprimer_devis, modifier_devis,
                            supprimer_devis_client)


# ═══════════════════════════════════════════════════════════════════
#  PALETTE MODERNE (blanc/vert épuré)
# ═══════════════════════════════════════════════════════════════════
C_BG       = "#F5F7F5"      # blanc cassé
C_SIDEBAR  = "#FFFFFF"      # blanc
C_PANEL    = "#FFFFFF"      # blanc
C_CARD     = "#FAFCFA"      # blanc très clair
C_ACCENT1  = "#2E7D32"      # vert foncé
C_ACCENT2  = "#4CAF50"      # vert moyen
C_ACCENT3  = "#81C784"      # vert clair
C_DANGER   = "#DC3545"      # rouge moderne
C_DANGER_H = "#C82333"      
C_WARN     = "#FFC107"      # jaune
C_TEXT     = "#212529"      # gris foncé
C_TEXT_SUB = "#6C757D"      # gris moyen
C_TEXT_DIM = "#ADB5BD"      # gris clair
C_ENTRY_BG = "#FFFFFF"      # blanc
C_ENTRY_FG = "#212529"      
C_BORDER   = "#DEE2E6"      # gris bordure
C_SEP      = "#E9ECEF"      
C_STR_A    = "#FFFFFF"      
C_STR_B    = "#F8F9FA"      
FONT       = "Segoe UI"

current_user = None


# ═══════════════════════════════════════════════════════════════════
#  FENETRE
# ═══════════════════════════════════════════════════════════════════
app = tk.Tk()
app.title("🌿 Paysagisme Studio")
app.geometry("1200x720")
app.minsize(920, 620)
app.configure(bg=C_BG)


# ═══════════════════════════════════════════════════════════════════
#  STYLE TTK
# ═══════════════════════════════════════════════════════════════════
sty = ttk.Style()
sty.theme_use("default")
sty.configure("Treeview", background=C_CARD, fieldbackground=C_CARD,
               foreground=C_TEXT, rowheight=32, borderwidth=1,
               font=(FONT, 10))
sty.configure("Treeview.Heading", background=C_PANEL, foreground=C_ACCENT1,
               font=(FONT, 10, "bold"), relief="flat", borderwidth=0, padding=6)
sty.map("Treeview",
        background=[("selected", C_ACCENT2)],
        foreground=[("selected", "white")])
sty.map("Treeview.Heading", background=[("active", C_SEP)])
sty.configure("Vertical.TScrollbar", background=C_PANEL,
               troughcolor=C_BG, arrowcolor=C_ACCENT1, borderwidth=0)


# ═══════════════════════════════════════════════════════════════════
#  HELPERS UI
# ═══════════════════════════════════════════════════════════════════
def make_entry(parent, placeholder="", password=False, width=35):
    """Entry stylisée sans padx/pady dans les kwargs"""
    kw = dict(
        bg=C_ENTRY_BG, 
        fg=C_ENTRY_FG,
        insertbackground=C_ACCENT1, 
        relief="solid",
        font=(FONT, 11), 
        highlightthickness=1,
        highlightbackground=C_BORDER, 
        highlightcolor=C_ACCENT1, 
        bd=1,
        width=width
    )
    if password:
        kw["show"] = "•"
    e = tk.Entry(parent, **kw)

    if placeholder and not password:
        e.insert(0, placeholder)
        e.config(fg=C_TEXT_DIM)
        def on_in(ev):
            if e.get() == placeholder:
                e.delete(0, "end")
                e.config(fg=C_ENTRY_FG)
        def on_out(ev):
            if e.get() == "":
                e.insert(0, placeholder)
                e.config(fg=C_TEXT_DIM)
        e.bind("<FocusIn>",  on_in)
        e.bind("<FocusOut>", on_out)
    return e


def make_button(parent, text, command, color=C_ACCENT1, text_color="white", width=18):
    h = C_ACCENT3 if color == C_ACCENT1 else (C_DANGER_H if color == C_DANGER else C_ACCENT2)
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=text_color,
                    activebackground=h, activeforeground="white",
                    font=(FONT, 11, "bold"), relief="flat",
                    cursor="hand2", width=width, bd=0, pady=9)
    btn.bind("<Enter>", lambda e: btn.config(bg=h))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def lbl(parent, text, size=10, bold=False, color=None, **kw):
    return tk.Label(parent, text=text,
                    font=(FONT, size, "bold" if bold else "normal"),
                    bg=parent["bg"], fg=color or C_TEXT, **kw)


def section_title(parent, text):
    f = tk.Frame(parent, bg=parent["bg"])
    f.pack(fill="x", padx=28, pady=(14, 3))
    tk.Label(f, text=text, font=(FONT, 10, "bold"),
             bg=parent["bg"], fg=C_ACCENT1).pack(side="left")
    tk.Frame(f, bg=C_SEP, height=1).pack(
        side="left", fill="x", expand=True, padx=(10, 0), pady=7)


def make_table(parent, columns, heights=6):
    wrapper = tk.Frame(parent, bg=C_BORDER)
    wrapper.pack(pady=4, padx=28, fill="x")
    inner = tk.Frame(wrapper, bg=C_CARD)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    tv = ttk.Treeview(inner, columns=columns, show="headings", height=heights)
    for c in columns:
        tv.heading(c, text=c.upper())
        tv.column(c, anchor="center", width=110, minwidth=50)
    sb = ttk.Scrollbar(inner, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    tv.tag_configure("A",       background=C_STR_A)
    tv.tag_configure("B",       background=C_STR_B)
    tv.tag_configure("ok",      foreground=C_ACCENT2)
    tv.tag_configure("refuse",  foreground=C_DANGER)
    tv.tag_configure("attente", foreground=C_WARN)
    return tv


def insert_row(tv, values):
    idx  = len(tv.get_children())
    stag = ""
    for v in values:
        sv = str(v).lower()
        if "accept" in sv: stag = "ok"
        elif "refus"  in sv: stag = "refuse"
        elif "attente" in sv: stag = "attente"
    stripe = "A" if idx % 2 == 0 else "B"
    tv.insert("", "end", values=values,
              tags=(stripe, stag) if stag else (stripe,))


def build_left_deco(parent):
    tk.Frame(parent, bg=C_ACCENT1, width=5).place(x=0, y=0, relheight=1)
    left = tk.Frame(parent, bg=C_SIDEBAR)
    left.place(x=5, y=0, relwidth=0.38, relheight=1)
    tk.Label(left, text="🌿", font=("Segoe UI", 72),
             bg=C_SIDEBAR, fg=C_ACCENT1).place(relx=0.5, rely=0.28, anchor="center")
    tk.Label(left, text="PAYSAGISME\nSTUDIO",
             font=(FONT, 20, "bold"), bg=C_SIDEBAR, fg=C_TEXT,
             justify="center").place(relx=0.5, rely=0.46, anchor="center")
    tk.Label(left, text="Gestion · Devis · Clients",
             font=(FONT, 9), bg=C_SIDEBAR, fg=C_TEXT_SUB
             ).place(relx=0.5, rely=0.54, anchor="center")
    tk.Frame(parent, bg=C_BORDER, width=1).place(relx=0.38, x=5, y=0, relheight=1)


def build_sidebar(parent, items, on_logout):
    sb = tk.Frame(parent, bg=C_SIDEBAR, width=220)
    sb.pack(side="left", fill="y")
    sb.pack_propagate(False)
    tk.Frame(sb, bg=C_ACCENT1, height=4).pack(fill="x")
    tk.Label(sb, text="🌿  PAYSAGISME",
             font=(FONT, 11, "bold"), bg=C_SIDEBAR, fg=C_ACCENT1).pack(pady=(16, 4))
    tk.Frame(sb, bg=C_SEP, height=1).pack(fill="x", padx=16, pady=4)
    for icon, label, cmd in items:
        row = tk.Frame(sb, bg=C_SIDEBAR, cursor="hand2")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"  {icon}  {label}",
                 font=(FONT, 10), bg=C_SIDEBAR, fg=C_TEXT, anchor="w"
                 ).pack(fill="x", ipady=10, ipadx=8)
        for w in [row] + row.winfo_children():
            w.bind("<Enter>",    lambda e, r=row: r.config(bg=C_SEP))
            w.bind("<Leave>",    lambda e, r=row: r.config(bg=C_SIDEBAR))
            w.bind("<Button-1>", lambda e, c=cmd: c())
    tk.Frame(sb, bg=C_SIDEBAR).pack(fill="both", expand=True)
    tk.Frame(sb, bg=C_SEP, height=1).pack(fill="x", padx=16)
    btn = tk.Button(sb, text="⏻  Déconnexion", command=on_logout,
                    bg=C_SIDEBAR, fg=C_TEXT_DIM,
                    activebackground=C_DANGER, activeforeground="white",
                    font=(FONT, 9, "bold"), relief="flat", cursor="hand2", bd=0, pady=10)
    btn.pack(fill="x", padx=8, pady=10)
    btn.bind("<Enter>", lambda e: btn.config(bg=C_DANGER, fg="white"))
    btn.bind("<Leave>", lambda e: btn.config(bg=C_SIDEBAR, fg=C_TEXT_DIM))
    return sb


# ═══════════════════════════════════════════════════════════════════
#  CONTENEUR
# ═══════════════════════════════════════════════════════════════════
container = tk.Frame(app, bg=C_BG)
container.pack(fill="both", expand=True)


def show(page):
    page.tkraise()


# ════════════════════════════════════════════════════════════════════
#  ░░  LOGIN PAGE  ░░
# ════════════════════════════════════════════════════════════════════
login_page = tk.Frame(container, bg=C_BG)
login_page.place(relwidth=1, relheight=1)
build_left_deco(login_page)

right_login = tk.Frame(login_page, bg=C_BG)
right_login.place(relx=0.38, x=6, y=0, relwidth=0.62, relheight=1)

login_card = tk.Frame(right_login, bg=C_PANEL,
                      highlightthickness=1, highlightbackground=C_BORDER, relief="solid")
login_card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=450)

tk.Frame(login_card, bg=C_ACCENT1, height=4).pack(fill="x")
lbl(login_card, "CONNEXION", size=18, bold=True).pack(pady=(25, 5))
lbl(login_card, "Entrez vos identifiants", size=10, color=C_TEXT_SUB).pack(pady=(0, 20))

lbl(login_card, "EMAIL", size=9, color=C_TEXT_SUB).pack(anchor="w", padx=40)
login_email = make_entry(login_card, placeholder="votre@email.fr", width=35)
login_email.pack(pady=(5, 12), padx=40, fill="x")

lbl(login_card, "MOT DE PASSE", size=9, color=C_TEXT_SUB).pack(anchor="w", padx=40)
login_pwd = make_entry(login_card, password=True, width=35)
login_pwd.pack(pady=(5, 8), padx=40, fill="x")

login_err = lbl(login_card, "", size=9, color=C_DANGER)
login_err.pack()

tk.Frame(login_card, bg=C_SEP, height=1).pack(fill="x", padx=40, pady=(15, 10))
lbl(login_card, "Pas encore de compte ?", size=9, color=C_TEXT_DIM).pack()


# ════════════════════════════════════════════════════════════════════
#  ░░  INSCRIPTION PAGE  ░░
# ════════════════════════════════════════════════════════════════════
register_page = tk.Frame(container, bg=C_BG)
register_page.place(relwidth=1, relheight=1)
build_left_deco(register_page)

right_reg = tk.Frame(register_page, bg=C_BG)
right_reg.place(relx=0.38, x=6, y=0, relwidth=0.62, relheight=1)

reg_card = tk.Frame(right_reg, bg=C_PANEL,
                    highlightthickness=1, highlightbackground=C_BORDER, relief="solid")
reg_card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=580)

tk.Frame(reg_card, bg=C_ACCENT2, height=4).pack(fill="x")
lbl(reg_card, "CRÉER UN COMPTE", size=16, bold=True).pack(pady=(20, 5))
lbl(reg_card, "Rejoignez Paysagisme Studio", size=10, color=C_TEXT_SUB).pack(pady=(0, 15))

reg_grid = tk.Frame(reg_card, bg=C_PANEL)
reg_grid.pack(padx=30, fill="x")

reg_fields = {}

def reg_field(row, col, label_text, key, ph="", pw=False, span=1):
    c = col * 2
    tk.Label(reg_grid, text=label_text, font=(FONT, 8, "bold"),
             bg=C_PANEL, fg=C_TEXT_SUB).grid(
        row=row*2, column=c, columnspan=span*2,
        sticky="w", pady=(0, 2), padx=(0, 16))
    e = make_entry(reg_grid, placeholder=ph, password=pw, width=22 if span == 1 else 48)
    e.grid(row=row*2+1, column=c, columnspan=span*2,
           sticky="ew", pady=(0, 10), padx=(0, 16))
    reg_fields[key] = e

reg_field(0, 0, "NOM *",           "nom",    "Dupont")
reg_field(0, 1, "PRÉNOM *",        "prenom", "Jean")
reg_field(1, 0, "EMAIL *",         "email",  "jean@mail.fr", span=2)
reg_field(2, 0, "MOT DE PASSE *",  "mdp",    pw=True)
reg_field(2, 1, "CONFIRMATION *",  "mdp2",   pw=True)
reg_field(3, 0, "TÉLÉPHONE",       "tel",    "0612345678")
reg_field(3, 1, "VILLE",           "ville",  "Lyon")

reg_status = lbl(reg_card, "", size=9, color=C_ACCENT2)
reg_status.pack(pady=(2, 4), padx=30, anchor="w")


def do_register():
    nom    = reg_fields["nom"].get().strip()
    prenom = reg_fields["prenom"].get().strip()
    email  = reg_fields["email"].get().strip()
    mdp    = reg_fields["mdp"].get().strip()
    mdp2   = reg_fields["mdp2"].get().strip()
    tel    = reg_fields["tel"].get().strip()
    ville  = reg_fields["ville"].get().strip()

    PH = {"Dupont", "Jean", "jean@mail.fr", "0612345678", "Lyon", ""}

    if not nom or nom in PH:
        reg_status.config(text="⚠ Nom requis", fg=C_DANGER); return
    if not prenom or prenom in PH:
        reg_status.config(text="⚠ Prénom requis", fg=C_DANGER); return
    if not email or "@" not in email or email in PH:
        reg_status.config(text="⚠ Email invalide", fg=C_DANGER); return
    if not mdp:
        reg_status.config(text="⚠ Mot de passe requis", fg=C_DANGER); return
    if len(mdp) < 4:
        reg_status.config(text="⚠ Mot de passe trop court (4 min.)", fg=C_DANGER); return
    if mdp != mdp2:
        reg_status.config(text="⚠ Les mots de passe ne correspondent pas", fg=C_DANGER); return
    if email_existe(email):
        reg_status.config(text="⚠ Cet email est déjà utilisé", fg=C_DANGER); return
    
    # Vérifier téléphone unique
    if tel and tel not in PH:
        if telephone_existe(tel):
            reg_status.config(text="⚠ Ce numéro de téléphone est déjà utilisé", fg=C_DANGER); return

    tel_v   = "" if tel in PH else tel
    ville_v = "" if ville in PH else ville
    
    try:
        inscrire_client(nom, prenom, tel_v, email, ville_v, mdp)
        reg_status.config(text=f"✔ Compte créé ! Connexion possible.", fg=C_ACCENT2)
        app.after(1600, lambda: show(login_page))
    except ValueError as e:
        reg_status.config(text=f"⚠ {str(e)}", fg=C_DANGER)


make_button(reg_card, "✔  Créer mon compte", do_register,
            color=C_ACCENT2, text_color="white", width=24
            ).pack(pady=(10, 8), padx=30, anchor="w")

back_row = tk.Frame(reg_card, bg=C_PANEL)
back_row.pack(padx=30, anchor="w")
lbl(back_row, "Déjà un compte ? ", size=9, color=C_TEXT_DIM).pack(side="left")
back_lnk = tk.Label(back_row, text="Se connecter →",
                    font=(FONT, 9, "bold"), bg=C_PANEL,
                    fg=C_ACCENT1, cursor="hand2")
back_lnk.pack(side="left")
back_lnk.bind("<Button-1>", lambda e: show(login_page))
back_lnk.bind("<Enter>",    lambda e: back_lnk.config(fg=C_ACCENT2))
back_lnk.bind("<Leave>",    lambda e: back_lnk.config(fg=C_ACCENT1))


# ════════════════════════════════════════════════════════════════════
#  ░░  ADMIN PAGE  ░░
# ════════════════════════════════════════════════════════════════════
admin_page = tk.Frame(container, bg=C_BG)
admin_page.place(relwidth=1, relheight=1)

adm_frames = {}

def switch_admin(name):
    for f in adm_frames.values(): f.pack_forget()
    adm_frames[name].pack(fill="both", expand=True)


def logout():
    global current_user
    current_user = None
    login_email.delete(0, "end")
    login_email.insert(0, "votre@email.fr")
    login_email.config(fg=C_TEXT_DIM)
    login_pwd.delete(0, "end")
    login_err.config(text="")
    show(login_page)


adm_wrap = tk.Frame(admin_page, bg=C_BG)
adm_wrap.pack(fill="both", expand=True)

build_sidebar(adm_wrap,
    [("👥", "Clients",        lambda: switch_admin("clients")),
     ("📋", "Devis",          lambda: switch_admin("devis")),
     ("➕", "Ajouter client", lambda: switch_admin("add_client"))],
    logout)

adm_main = tk.Frame(adm_wrap, bg=C_BG)
adm_main.pack(side="left", fill="both", expand=True)

adm_hdr = tk.Frame(adm_main, bg=C_PANEL, height=52)
adm_hdr.pack(fill="x"); adm_hdr.pack_propagate(False)
lbl(adm_hdr, "🛠  ESPACE ADMIN", size=14, bold=True, color=C_ACCENT1
    ).pack(side="left", padx=22, pady=12)
tk.Frame(adm_hdr, bg=C_ACCENT1, width=3).pack(side="left", fill="y", pady=10)
adm_subtitle = lbl(adm_hdr, "Tableau de bord", size=9, color=C_TEXT_SUB)
adm_subtitle.pack(side="left", padx=14)
clock_a = lbl(adm_hdr, "", size=9, color=C_TEXT_DIM)
clock_a.pack(side="right", padx=18)

# ── Clients ─────────────────────────────────────────────────────────
f_cli = tk.Frame(adm_main, bg=C_BG)
adm_frames["clients"] = f_cli
section_title(f_cli, "◈  CLIENTS ENREGISTRÉS")
COL_CLI = ("ID", "Nom", "Prénom", "Téléphone", "Email", "Adresse", "Rôle")
tbl_cli = make_table(f_cli, COL_CLI, heights=8)
for col, w in zip(COL_CLI, [40, 100, 100, 115, 210, 190, 70]):
    tbl_cli.column(col, width=w)
btn_cli_row = tk.Frame(f_cli, bg=C_BG)
btn_cli_row.pack(padx=28, pady=6, anchor="w")

def load_clients():
    for i in tbl_cli.get_children(): tbl_cli.delete(i)
    for c in afficher_clients(): insert_row(tbl_cli, c)

def delete_client():
    sel  = tbl_cli.focus()
    data = tbl_cli.item(sel, "values")
    if not data: return
    if data[6] == "admin":
        messagebox.showwarning("Interdit", "Impossible de supprimer un admin."); return
    if messagebox.askyesno("Confirmer", f"Supprimer {data[1]} {data[2]} et tous ses devis ?"):
        supprimer_client(data[0]); load_clients(); load_devis()

make_button(btn_cli_row, "⌫  Supprimer client", delete_client,
            color=C_DANGER, text_color="white", width=20).pack(side="left")

# ── Devis admin ──────────────────────────────────────────────────────
f_dev = tk.Frame(adm_main, bg=C_BG)
adm_frames["devis"] = f_dev
section_title(f_dev, "◈  TOUS LES DEVIS")
COL_DEV = ("ID", "Client", "Description", "Montant €", "Statut", "Date")
tbl_dev = make_table(f_dev, COL_DEV, heights=10)
for col, w in zip(COL_DEV, [45, 155, 310, 90, 100, 90]):
    tbl_dev.column(col, width=w)
btn_dev_row = tk.Frame(f_dev, bg=C_BG)
btn_dev_row.pack(padx=28, pady=6, anchor="w")

def load_devis():
    for i in tbl_dev.get_children(): tbl_dev.delete(i)
    for d in afficher_devis(): insert_row(tbl_dev, d)

def change_statut(s):
    sel  = tbl_dev.focus()
    data = tbl_dev.item(sel, "values")
    if data: changer_statut(data[0], s); load_devis()

def del_devis_admin():
    sel  = tbl_dev.focus()
    data = tbl_dev.item(sel, "values")
    if data: supprimer_devis(data[0]); load_devis()

make_button(btn_dev_row, "✔  Accepter",   lambda: change_statut("Accepté"),
            color="#2E7D32", text_color="white", width=13).pack(side="left", padx=(0,6))
make_button(btn_dev_row, "✘  Refuser",    lambda: change_statut("Refusé"),
            color=C_DANGER, text_color="white",    width=13).pack(side="left", padx=(0,6))
make_button(btn_dev_row, "⟳  En attente", lambda: change_statut("En attente"),
            color=C_WARN,   text_color=C_TEXT,       width=14).pack(side="left", padx=(0,6))
make_button(btn_dev_row, "⌫  Supprimer",  del_devis_admin,
            color="#6C757D", text_color="white", width=13).pack(side="left")

# ── Ajouter client (admin) ───────────────────────────────────────────
f_add = tk.Frame(adm_main, bg=C_BG)
adm_frames["add_client"] = f_add
section_title(f_add, "◈  AJOUTER UN CLIENT")
add_card = tk.Frame(f_add, bg=C_PANEL,
                    highlightthickness=1, highlightbackground=C_BORDER, relief="solid")
add_card.pack(padx=28, pady=6, fill="x")
add_inner = tk.Frame(add_card, bg=C_PANEL)
add_inner.pack(padx=24, pady=18, anchor="w")
add_fields = {}

def add_field(row, col, label_text, key, ph="", pw=False):
    c = col * 2
    tk.Label(add_inner, text=label_text, font=(FONT, 8, "bold"),
             bg=C_PANEL, fg=C_TEXT_SUB).grid(
        row=row*2, column=c, sticky="w", pady=(0,2), padx=(0,24))
    e = make_entry(add_inner, placeholder=ph, password=pw, width=26)
    e.grid(row=row*2+1, column=c, sticky="ew", pady=(0,12), padx=(0,24))
    add_fields[key] = e

add_field(0, 0, "NOM *",          "nom",    "Dupont")
add_field(0, 1, "PRÉNOM",         "prenom", "Jean")
add_field(1, 0, "EMAIL *",        "email",  "jean@mail.fr")
add_field(1, 1, "TÉLÉPHONE",      "tel",    "0612345678")
add_field(2, 0, "ADRESSE",        "adresse","Lyon")
add_field(2, 1, "MOT DE PASSE *", "mdp",    pw=True)

tk.Label(add_inner, text="RÔLE", font=(FONT, 8, "bold"),
         bg=C_PANEL, fg=C_TEXT_SUB).grid(row=6, column=0, sticky="w", pady=(0,2))
role_var = tk.StringVar(value="client")
rf = tk.Frame(add_inner, bg=C_PANEL)
rf.grid(row=7, column=0, sticky="w", pady=(0,12), columnspan=4)
for rv, rl in [("client","Client"),("admin","Admin")]:
    tk.Radiobutton(rf, text=rl, variable=role_var, value=rv,
                   bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG,
                   activebackground=C_PANEL, activeforeground=C_ACCENT1,
                   font=(FONT, 10)).pack(side="left", padx=(0,16))

add_status = lbl(add_inner, "", size=9, color=C_ACCENT2)
add_status.grid(row=8, column=0, columnspan=4, sticky="w", pady=(0,8))

def do_add_client():
    nom   = add_fields["nom"].get().strip()
    email = add_fields["email"].get().strip()
    mdp   = add_fields["mdp"].get().strip()
    tel   = add_fields["tel"].get().strip()
    PH    = {"Dupont","jean@mail.fr",""}
    if not nom or nom in PH:
        add_status.config(text="⚠ Nom requis", fg=C_DANGER); return
    if not email or "@" not in email or email in PH:
        add_status.config(text="⚠ Email invalide", fg=C_DANGER); return
    if not mdp:
        add_status.config(text="⚠ Mot de passe requis", fg=C_DANGER); return
    if email_existe(email):
        add_status.config(text="⚠ Email déjà utilisé", fg=C_DANGER); return
    
    # Vérifier téléphone unique
    if tel and tel not in PH:
        if telephone_existe(tel):
            add_status.config(text="⚠ Téléphone déjà utilisé", fg=C_DANGER); return
    
    try:
        ajouter_client(add_fields["nom"].get().strip(),
                       add_fields["prenom"].get().strip(),
                       tel if tel not in PH else None,
                       email,
                       add_fields["adresse"].get().strip(),
                       role_var.get(), mdp)
        load_clients()
        add_status.config(text="✔ Client créé.", fg=C_ACCENT2)
        for e in add_fields.values(): e.delete(0, "end")
    except ValueError as e:
        add_status.config(text=f"⚠ {str(e)}", fg=C_DANGER)

make_button(add_inner, "➕  Créer le client", do_add_client,
            color=C_ACCENT1, text_color="white", width=22
            ).grid(row=9, column=0, sticky="w", columnspan=2)


# ════════════════════════════════════════════════════════════════════
#  ░░  CLIENT PAGE  ░░
# ════════════════════════════════════════════════════════════════════
client_page = tk.Frame(container, bg=C_BG)
client_page.place(relwidth=1, relheight=1)

cli_frames = {}

def switch_client(name):
    for f in cli_frames.values(): f.pack_forget()
    cli_frames[name].pack(fill="both", expand=True)

cli_wrap = tk.Frame(client_page, bg=C_BG)
cli_wrap.pack(fill="both", expand=True)

build_sidebar(cli_wrap,
    [("📋", "Mes devis",        lambda: switch_client("mes_devis")),
     ("✏️", "Nouveau devis",    lambda: switch_client("nouveau_devis")),
     ("👤", "Mon profil",       lambda: switch_client("mon_profil")),
     ("🗑️", "Supprimer compte", lambda: switch_client("supprimer_compte"))],
    logout)

cli_main = tk.Frame(cli_wrap, bg=C_BG)
cli_main.pack(side="left", fill="both", expand=True)

cli_hdr = tk.Frame(cli_main, bg=C_PANEL, height=52)
cli_hdr.pack(fill="x"); cli_hdr.pack_propagate(False)
lbl(cli_hdr, "🌱  ESPACE CLIENT", size=14, bold=True, color=C_ACCENT1
    ).pack(side="left", padx=22, pady=12)
tk.Frame(cli_hdr, bg=C_ACCENT1, width=3).pack(side="left", fill="y", pady=10)
cli_welcome = lbl(cli_hdr, "Bienvenue", size=9, color=C_TEXT_SUB)
cli_welcome.pack(side="left", padx=14)
clock_c = lbl(cli_hdr, "", size=9, color=C_TEXT_DIM)
clock_c.pack(side="right", padx=18)

# ── Mes devis ─────────────────────────────────────────────────────────
f_mes = tk.Frame(cli_main, bg=C_BG)
cli_frames["mes_devis"] = f_mes
section_title(f_mes, "◈  MES DEVIS")
tbl_mes = make_table(f_mes, COL_DEV, heights=10)
for col, w in zip(COL_DEV, [45, 150, 330, 90, 100, 90]):
    tbl_mes.column(col, width=w)

def load_client_devis():
    for i in tbl_mes.get_children(): tbl_mes.delete(i)
    if current_user:
        for d in afficher_devis_client(current_user[0]):
            insert_row(tbl_mes, d)

lbl(f_mes, "ℹ  Contactez-nous pour modifier ou annuler un devis.",
    size=8, color=C_TEXT_DIM).pack(anchor="w", padx=28, pady=(2, 0))

# ── Nouveau devis ─────────────────────────────────────────────────────
f_ndev = tk.Frame(cli_main, bg=C_BG)
cli_frames["nouveau_devis"] = f_ndev
section_title(f_ndev, "◈  NOUVELLE DEMANDE DE DEVIS")

ndev_card = tk.Frame(f_ndev, bg=C_PANEL,
                     highlightthickness=1, highlightbackground=C_BORDER, relief="solid")
ndev_card.pack(padx=28, pady=6, fill="x")
ndev_in = tk.Frame(ndev_card, bg=C_PANEL)
ndev_in.pack(padx=24, pady=20, anchor="w")

lbl(ndev_in, "DESCRIPTION DU PROJET", size=9, color=C_TEXT_SUB).pack(anchor="w", pady=(0,3))
entry_desc = make_entry(ndev_in, placeholder="Ex : Taille de haie, création de jardin...", width=60)
entry_desc.pack(fill="x", pady=(0,12))

lbl(ndev_in, "MONTANT ESTIMÉ (€)", size=9, color=C_TEXT_SUB).pack(anchor="w", pady=(0,3))
entry_montant = make_entry(ndev_in, placeholder="0.00", width=20)
entry_montant.pack(anchor="w", pady=(0,16))

devis_status = lbl(ndev_in, "", size=9, color=C_ACCENT2)
devis_status.pack(anchor="w", pady=(0,6))

def create_devis():
    desc = entry_desc.get().strip()
    mont = entry_montant.get().strip()
    PH   = {"Ex : Taille de haie, création de jardin...", "0.00", ""}
    if not desc or desc in PH:
        devis_status.config(text="⚠ Description requise", fg=C_DANGER); return
    try: val = float(mont.replace(",", "."))
    except ValueError:
        devis_status.config(text="⚠ Montant invalide", fg=C_DANGER); return
    ajouter_devis(current_user[0], desc, val, "En attente")
    load_client_devis()
    entry_desc.delete(0, "end"); entry_montant.delete(0, "end")
    devis_status.config(text="✔ Demande envoyée — statut : En attente.", fg=C_ACCENT2)

make_button(ndev_in, "✉  Envoyer le devis", create_devis,
            color=C_ACCENT1, text_color="white", width=22).pack(anchor="w")

# ── Mon profil ────────────────────────────────────────────────────────
f_profil = tk.Frame(cli_main, bg=C_BG)
cli_frames["mon_profil"] = f_profil

section_title(f_profil, "◈  MON PROFIL")

profil_card = tk.Frame(f_profil, bg=C_PANEL,
                       highlightthickness=1, highlightbackground=C_BORDER, relief="solid")
profil_card.pack(padx=28, pady=6, fill="x")
profil_inner = tk.Frame(profil_card, bg=C_PANEL)
profil_inner.pack(padx=30, pady=20)

profil_fields = {}

def create_profil_field(row, label, key, is_password=False):
    tk.Label(profil_inner, text=label, font=(FONT, 9, "bold"),
             bg=C_PANEL, fg=C_TEXT_SUB).grid(row=row, column=0, sticky="w", pady=(10, 2))
    e = make_entry(profil_inner, password=is_password, width=40)
    e.grid(row=row, column=1, sticky="ew", pady=(10, 2), padx=(20, 0))
    profil_fields[key] = e

def load_profil():
    info = get_client_info(current_user[0])
    if info:
        profil_fields["nom"].delete(0, "end")
        profil_fields["nom"].insert(0, info[1])
        profil_fields["prenom"].delete(0, "end")
        profil_fields["prenom"].insert(0, info[2])
        profil_fields["tel"].delete(0, "end")
        profil_fields["tel"].insert(0, info[3] if info[3] else "")
        profil_fields["email"].delete(0, "end")
        profil_fields["email"].insert(0, info[4])
        profil_fields["adresse"].delete(0, "end")
        profil_fields["adresse"].insert(0, info[5] if info[5] else "")
        profil_fields["mdp"].delete(0, "end")

create_profil_field(0, "NOM", "nom")
create_profil_field(1, "PRÉNOM", "prenom")
create_profil_field(2, "TÉLÉPHONE", "tel")
create_profil_field(3, "EMAIL", "email")
create_profil_field(4, "ADRESSE", "adresse")
create_profil_field(5, "NOUVEAU MOT DE PASSE (laisser vide pour ne pas changer)", "mdp", True)

profil_status = lbl(profil_inner, "", size=9, color=C_ACCENT2)
profil_status.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

def save_profil():
    global current_user
    try:
        modifier_profil(
            current_user[0],
            profil_fields["nom"].get().strip(),
            profil_fields["prenom"].get().strip(),
            profil_fields["tel"].get().strip(),
            profil_fields["email"].get().strip(),
            profil_fields["adresse"].get().strip(),
            profil_fields["mdp"].get().strip() if profil_fields["mdp"].get().strip() else None
        )
        profil_status.config(text="✔ Profil mis à jour avec succès", fg=C_ACCENT2)
        new_info = get_client_info(current_user[0])
        current_user = new_info
        cli_welcome.config(text=f"Bienvenue, {new_info[2]} {new_info[1]}")
    except ValueError as e:
        profil_status.config(text=f"⚠ {str(e)}", fg=C_DANGER)

btn_frame = tk.Frame(profil_inner, bg=C_PANEL)
btn_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
make_button(btn_frame, "💾  Enregistrer", save_profil, width=20).pack(side="left", padx=5)
make_button(btn_frame, "🔄  Annuler", load_profil, color=C_TEXT_DIM, width=20).pack(side="left", padx=5)

# ── Supprimer compte ──────────────────────────────────────────────────
f_delete = tk.Frame(cli_main, bg=C_BG)
cli_frames["supprimer_compte"] = f_delete

section_title(f_delete, "◈  SUPPRIMER MON COMPTE")

delete_card = tk.Frame(f_delete, bg=C_PANEL,
                       highlightthickness=1, highlightbackground=C_BORDER, relief="solid")
delete_card.pack(padx=28, pady=20, fill="x")

delete_inner = tk.Frame(delete_card, bg=C_PANEL)
delete_inner.pack(padx=30, pady=30)

lbl(delete_inner, "⚠️  ATTENTION : Cette action est irréversible !", 
    size=12, bold=True, color=C_DANGER).pack(pady=(0, 15))
lbl(delete_inner, "La suppression de votre compte entraînera :", 
    size=10, color=C_TEXT).pack(anchor="w", pady=5)
lbl(delete_inner, "• La perte de tous vos devis", 
    size=9, color=C_TEXT_SUB).pack(anchor="w", pady=2)
lbl(delete_inner, "• La perte de vos informations personnelles", 
    size=9, color=C_TEXT_SUB).pack(anchor="w", pady=2)
lbl(delete_inner, "• L'impossibilité de récupérer vos données", 
    size=9, color=C_TEXT_SUB).pack(anchor="w", pady=2)

tk.Frame(delete_inner, bg=C_SEP, height=1).pack(fill="x", pady=15)

lbl(delete_inner, "Pour confirmer, tapez 'SUPPRIMER' ci-dessous :", 
    size=9, color=C_TEXT).pack(anchor="w", pady=5)
confirm_entry = make_entry(delete_inner, width=30)
confirm_entry.pack(anchor="w", pady=(0, 15))

delete_status = lbl(delete_inner, "", size=9, color=C_ACCENT2)
delete_status.pack(anchor="w", pady=5)

def confirm_delete_account():
    if confirm_entry.get().strip() != "SUPPRIMER":
        delete_status.config(text="⚠ Tapez 'SUPPRIMER' pour confirmer", fg=C_DANGER)
        return
    
    if messagebox.askyesno("Confirmation définitive", 
                           "Êtes-vous ABSOLUMENT sûr de vouloir supprimer votre compte ?\n"
                           "Cette action est irréversible et supprimera tous vos devis."):
        supprimer_compte_client(current_user[0])
        messagebox.showinfo("Compte supprimé", "Votre compte a été supprimé.\nMerci d'avoir utilisé Paysagisme Studio.")
        logout()

make_button(delete_inner, "🗑️  SUPPRIMER DÉFINITIVEMENT MON COMPTE", 
            confirm_delete_account, color=C_DANGER, text_color="white", width=35).pack(pady=10)


# ═══════════════════════════════════════════════════════════════════
#  BARRE DE STATUT
# ═══════════════════════════════════════════════════════════════════
status_bar = tk.Frame(app, bg=C_SIDEBAR, height=28)
status_bar.pack(fill="x", side="bottom")
tk.Frame(status_bar, bg=C_ACCENT1, height=2).pack(fill="x", side="top")
status_lbl = tk.Label(status_bar, text="Prêt",
                      font=(FONT, 8), bg=C_SIDEBAR, fg=C_TEXT_DIM, anchor="w")
status_lbl.pack(side="left", padx=12)
clock_bar = tk.Label(status_bar, text="",
                     font=(FONT, 8), bg=C_SIDEBAR, fg=C_TEXT_DIM, anchor="e")
clock_bar.pack(side="right", padx=12)

def tick():
    now = datetime.datetime.now()
    clock_bar.config(text=now.strftime("%A %d %B %Y  —  %H:%M:%S"))
    hm = now.strftime("%H:%M")
    if 'clock_a' in globals():
        clock_a.config(text=hm)
    if 'clock_c' in globals():
        clock_c.config(text=hm)
    app.after(1000, tick)

tick()


# ═══════════════════════════════════════════════════════════════════
#  LOGIN + BOUTONS
# ═══════════════════════════════════════════════════════════════════
def login():
    global current_user
    email = login_email.get().strip()
    pwd   = login_pwd.get().strip()

    if not email or email == "votre@email.fr":
        login_err.config(text="⚠ Email requis"); return
    if not pwd:
        login_err.config(text="⚠ Mot de passe requis"); return

    user = login_client(email, pwd)
    if user:
        current_user = user
        login_err.config(text="")
        status_lbl.config(text=f"Connecté : {user[1]} {user[2]}  [{user[6]}]")
        if user[6] == "admin":
            adm_subtitle.config(text=f"Connecté : {user[1]} {user[2]}")
            switch_admin("clients"); show(admin_page)
            load_clients(); load_devis()
        else:
            cli_welcome.config(text=f"Bienvenue, {user[2]} {user[1]}")
            switch_client("mes_devis"); show(client_page)
            load_client_devis()
            load_profil()
    else:
        login_err.config(text="⚠ Email ou mot de passe incorrect")
        for w in [login_email, login_pwd]:
            w.config(highlightbackground=C_DANGER)
        app.after(1600, lambda: [
            w.config(highlightbackground=C_BORDER)
            for w in [login_email, login_pwd]])


def go_register():
    reg_status.config(text="")
    for e in reg_fields.values(): e.delete(0, "end")
    show(register_page)


make_button(login_card, "→  SE CONNECTER", login,
            color=C_ACCENT1, text_color="white", width=26
            ).pack(pady=(15, 5), padx=40, fill="x")

reg_link = tk.Label(login_card, text="Créer un compte →",
                    font=(FONT, 10, "bold"), bg=C_PANEL,
                    fg=C_ACCENT2, cursor="hand2")
reg_link.pack(pady=(5, 0))
reg_link.bind("<Button-1>", lambda e: go_register())
reg_link.bind("<Enter>",    lambda e: reg_link.config(fg=C_ACCENT1))
reg_link.bind("<Leave>",    lambda e: reg_link.config(fg=C_ACCENT2))

lbl(login_card, "© 2025 Paysagisme Studio", size=8, color=C_TEXT_DIM).pack(pady=(15, 0))

app.bind("<Return>", lambda e: login())


# ═══════════════════════════════════════════════════════════════════
#  START
# ═══════════════════════════════════════════════════════════════════
show(login_page)
app.mainloop()