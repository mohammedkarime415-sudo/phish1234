import nltk
from nltk.chat.util import Chat, reflections
import streamlit as st

# 1. Configuration de la page Streamlit (Correction effectuée)
st.set_page_config(
    page_title="Assistant Cybersécurité - Phishing",
    page_icon="🛡️",
    layout="centered"
)

# 2. Base de données des utilisateurs (Authentification simple)
USERS = {
    "admin": "password123",
    "analyste": "security2026"
}

def check_credentials(username, password):
    return USERS.get(username) == password

# Initialisation des états de session pour l'authentification et l'historique
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Écran de Connexion (Login)
if not st.session_state.authenticated:
    st.title("🛡️ Connexion à l'Assistant Cybersécurité")
    st.markdown("Veuillez saisir vos identifiants pour accéder au chatbot de sensibilisation au phishing.")

    with st.form("login_form"):
        username_input = st.text_input("Nom d'utilisateur")
        password_input = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("Se connecter")

        if submit_button:
            if check_credentials(username_input, password_input):
                st.session_state.authenticated = True
                st.session_state.user = username_input
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")
    st.stop()

# 4. Définition des paires de dialogue du Chatbot
pairs = [
    [r"Mon nom est (.*)", ["Bonjour %1, comment puis-je vous aider aujourd'hui ?"]],
    [r"Bonjour|salut|coucou", ["Bonjour ! En quoi puis-je vous éclairer sur le phishing aujourd'hui ?", "Salut ! Une question concernant la sécurité de vos e-mails ?"]],

    # --- Définition ---
    [r"(.*)(c'est quoi|qu'est[- ]ce que|définition|expliqu)(.*)(phishing|hame[cç]onnage)(.*)",
     ["Le **phishing (hameçonnage)** est une attaque où un fraudeur se fait passer pour un organisme de confiance (banque, administration, collègue...) afin de vous pousser à transmettre des informations sensibles : mots de passe, numéros de carte, codes de connexion.",
      "L'**hameçonnage** consiste à envoyer de faux messages (mail, SMS, appel) qui imitent une source fiable pour voler vos identifiants ou installer un logiciel malveillant."]],

    # --- Types d'attaques ---
    [r"(.*)(types?|sortes?|formes?|variantes?)(.*)(phishing|hame[cç]onnage)(.*)",
     ["Voici les principales variantes du phishing :\n\n- **Spear phishing** : Attaque ciblée sur une personne précise.\n- **Whaling** : Cible spécifiquement les dirigeants.\n- **Smishing** : Phishing réalisé par SMS.\n- **Vishing** : Phishing réalisé par appel téléphonique.\n- **Quishing** : Via un QR code piégé.\n- **Clone phishing** : Copie d'un vrai mail avec un lien modifié.\n- **BEC** : Fraude au faux président ou faux fournisseur."]],
    [r"(.*)spear[- ]?phishing(.*)",
     ["Le **spear phishing** est un hameçonnage ciblé : l'attaquant se renseigne sur sa victime (poste, collègues, projets) pour rédiger un message personnalisé et très crédible."]],
    [r"(.*)(smishing|sms)(.*)",
     ["Le **smishing** est du phishing par SMS (faux suivi de colis, faux remboursement). Ne cliquez pas sur le lien et ne répondez pas."]],
    [r"(.*)(vishing|appel|téléphone)(.*)",
     ["Le **vishing** est du phishing par téléphone. Un organisme sérieux ne vous demandera jamais un mot de passe ou un code reçu par SMS. Raccrochez immédiatement."]],
    [r"(.*)(qr code|quishing)(.*)",
     ["Le **quishing** utilise un QR code piégé redirigeant vers un faux site. Vérifiez toujours l'URL affichée avant de saisir des identifiants."]],
    [r"(.*)(faux président|bec|fraude au virement|faux fournisseur)(.*)",
     ["La **fraude au faux président (BEC)** vise à usurper l'identité d'un dirigeant pour obtenir un virement urgent. **Règle d'or** : toujours vérifier par un second canal officiel avant toute transaction."]],

    # --- Reconnaître un mail de phishing ---
    [r"(.*)(reconnaître|repérer|détecter|identifier|signes?|indices?)(.*)(phishing|hame[cç]onnage|mail|email|message)(.*)",
     ["**Signes d'alerte courants :**\n\n1. **Ton urgent ou menaçant** (« Compte suspendu sous 24h »).\n2. **Adresse expéditeur suspecte** (domaine légèrement modifié).\n3. **Fautes de frappe** ou mise en page approximative.\n4. **Lien piégé** (l'URL réelle diffère du texte affiché).\n5. **Pièce jointe inattendue**."]],
    [r"(.*)(lien|url)(.*)(vérifier|suspect|sûr|fiable|dangereux)(.*)",
     ["Survolez le lien avec votre curseur pour visualiser l'URL réelle. Vérifiez l'orthographe du domaine (`paypa1.com` vs `paypal.com`). En cas de doute, saisissez vous-même l'adresse sur votre navigateur."]],
    [r"(.*)(pièce jointe|piece jointe|attachement|fichier joint)(.*)",
     ["Méfiez-vous des pièces jointes inattendues (`.zip`, `.exe`, `.iso` ou documents Office demandant l'activation de macros). Confirmez l'envoi auprès de l'expéditeur via un autre canal."]],

    # --- Réaction après réception ---
    [r"j'ai reçu un (mail|email|sms|message|appel)(.*)",
     ["Ne cliquez sur aucun lien, ne téléchargez rien et ne répondez pas. Signalez le message à votre équipe sécurité ou via votre messagerie, puis supprimez-le."]],
    [r"(.*)(j'ai cliqué|j'ai clique|cliqué sur|clique sur)(.*)",
     ["**Procédure d'urgence :**\n\n1. Déconnectez l'appareil du réseau (Wi-Fi/Câble).\n2. Ne saisissez aucune donnée sur la page.\n3. Lancez une analyse antivirus complète.\n4. Changez vos mots de passe depuis un autre appareil sain.\n5. Prévenez votre service informatique / SOC."]],
    [r"(.*)(j'ai (donné|saisi|entré|renseigné)|mot de passe (volé|compromis))(.*)",
     ["Changez immédiatement le mot de passe concerné, activez la double authentification (MFA), et si vous avez fourni des données bancaires, faites opposition sans attendre."]],
    [r"(.*)(signaler|signalement|déclarer|reporter)(.*)",
     ["**Où signaler ?**\n- Auprès de votre service IT / SOC en entreprise.\n- Via le bouton « Signaler comme hameçonnage » de votre client e-mail.\n- En France : `signal-spam.fr`, `33700` (SMS), ou `cybermalveillance.gouv.fr`."]],

    # --- Prévention ---
    [r"(.*)(protéger|proteger|prévenir|éviter|prévention|se défendre|bonnes pratiques)(.*)",
     ["**Mesures de protection essentielles :**\n- Activer la **MFA** (Double authentification).\n- Utiliser un **gestionnaire de mots de passe**.\n- Maintenir vos systèmes et applications à jour.\n- Ne jamais céder à l'urgence d'un message."]],
    [r"(.*)(mfa|double authentification|2fa|authentification multifacteur)(.*)",
     ["La **MFA** ajoute une seconde couche de sécurité (application d'authentification, clé FIDO2). Même si votre mot de passe est volé, l'accès reste bloqué."]],
    [r"(.*)(gestionnaire de mots? de passe|password manager)(.*)",
     ["Un gestionnaire ne pré-remplit vos identifiants que sur le **vrai domaine**. S'il ne propose rien, vous êtes probablement sur un faux site !"]],
    [r"(.*)(formation|sensibilisation|simulation|entraînement)(.*)",
     ["La sensibilisation continue (simulations de phishing, ateliers réguliers) est le meilleur moyen de développer un réflexe de vigilance au quotidien."]],

    # --- Entreprise / Technique ---
    [r"(.*)(spf|dkim|dmarc)(.*)",
     ["**SPF, DKIM et DMARC** sont les trois piliers d'authentification des e-mails. Ils permettent de certifier l'expéditeur et de bloquer le spoofing (usurpation de domaine)."]],
    [r"(.*)(entreprise|organisation|société)(.*)(protéger|défendre|sécuriser)(.*)",
     ["Pour une entreprise : Filtrage e-mail renforcé, déploiement strict de SPF/DKIM/DMARC, MFA obligatoire, segmentation réseau, sauvegardes isolées (hors ligne) et sensibilisation du personnel."]],
    [r"(.*)(ransomware|rançongiciel|malware|logiciel malveillant)(.*)",
     ["Le phishing est le vecteur n°1 d'infection par **rançongiciel (ransomware)**. Un simple clic peut autoriser l'exécution d'un script malveillant."]],

    # --- Politesse et fin ---
    [r"(.*)(merci|thanks)(.*)", ["Avec plaisir ! Soyez vigilant face aux e-mails incertains.", "À votre service ! N'hésitez pas si vous avez d'autres questions."]],
    [r"(au revoir|bye|à bientôt|quit)", ["Au revoir ! Prenez garde aux liens et pièces jointes suspects."]],

    # --- Par défaut ---
    [r"(.*)", ["Je n'ai pas bien saisi votre demande. N'hésitez pas à me poser une question sur le phishing (définition, signes d'alerte, réaction à adopter, moyens de protection)."]],
]

chat = Chat(pairs, reflections)

# 5. Barre Latérale (Sidebar) de Navigation et Options
with st.sidebar:
    st.title("🛡️ Espace Sécurité")
    st.write(f"Connecté en tant que : **{st.session_state.user}**")
    st.divider()

    st.subheader("💡 Suggestions de questions")
    st.markdown("- *C'est quoi le phishing ?*")
    st.markdown("- *Comment reconnaître un mail suspect ?*")
    st.markdown("- *J'ai cliqué sur un lien, que faire ?*")
    st.markdown("- *C'est quoi le Smishing et le Vishing ?*")

    st.divider()
    if st.button("Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("Se déconnecter", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()

# 6. Interface Principale du Chatbot
st.title("🛡️ Assistant Cybersécurité")
st.caption("Posez vos questions sur les attaques par hameçonnage (phishing) et apprenez à vous en protéger.")

# Affichage de l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if user_prompt := st.chat_input("Posez votre question sur le phishing..."):
    # Affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Obtenir et afficher la réponse du chatbot
    bot_response = chat.respond(user_prompt)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)