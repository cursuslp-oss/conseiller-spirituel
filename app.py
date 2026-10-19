import streamlit as st
import anthropic

# --- Configuration de la page ---
st.set_page_config(
    page_title="Miroir Intérieur",
    page_icon="🪞",
    layout="centered"
)

# --- Import Google Fonts ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Inter:wght@200;300;400&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- Style personnalisé ---
st.markdown("""
<style>
    /* Fond bleu nuit profond */
    .stApp {
        background: linear-gradient(160deg, #060a14 0%, #0a0e1a 50%, #060a14 100%);
    }

    /* Typographie globale */
    .stApp, .stChatMessage p, .stMarkdown p {
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-weight: 300;
        letter-spacing: 0.01em;
        line-height: 1.8;
        color: #d0d4e8 !important;
    }

    /* Cacher le menu hamburger et le footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* En-tête personnalisé */
    .header-container {
        text-align: center;
        padding: 3rem 1rem 1.5rem 1rem;
        margin-bottom: 1rem;
    }
    .header-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 2.6rem;
        font-weight: 300;
        color: #e8e4e0;
        letter-spacing: 0.03em;
        margin-bottom: 0.6rem;
    }
    .header-line {
        width: 50px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2c46d, transparent);
        margin: 0.8rem auto;
    }
    .header-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        font-weight: 300;
        color: #c0c4d0 !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    /* Messages du chat - base */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0.8rem !important;
        padding-top: 2rem !important;
        margin-bottom: 0.6rem !important;
        border-radius: 12px !important;
        position: relative !important;
    }

    /* Messages de l'utilisateur */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background-color: rgba(201, 168, 76, 0.10) !important;
        border-left: 2px solid rgba(201, 168, 76, 0.4) !important;
    }

    /* Label "Ma question" */
    .stChatMessage[data-testid="stChatMessage-user"]::before {
        content: "Ma question";
        position: absolute;
        top: 0.5rem;
        left: 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.62rem;
        font-weight: 400;
        color: #c9a84c;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* Réponses de Miroir Intérieur */
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background-color: rgba(192, 200, 216, 0.06) !important;
        border-left: 2px solid rgba(192, 200, 216, 0.2) !important;
    }

    /* Label "Le miroir" */
    .stChatMessage[data-testid="stChatMessage-assistant"]::before {
        content: "Le miroir";
        position: absolute;
        top: 0.5rem;
        left: 1rem;
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 0.72rem;
        font-weight: 400;
        color: #9a9eb0;
        letter-spacing: 0.08em;
        font-style: italic;
    }

    /* Cacher les avatars */
    .stChatMessage [data-testid="chatAvatarIcon-assistant"],
    .stChatMessage [data-testid="chatAvatarIcon-user"],
    .stChatMessage .stAvatar,
    .stChatMessage [data-testid="stChatMessageAvatarAssistant"],
    .stChatMessage [data-testid="stChatMessageAvatarUser"],
    .stChatMessage img[alt="assistant avatar"],
    .stChatMessage img[alt="user avatar"],
    .stChatMessage svg {
        display: none !important;
    }

    /* Texte des messages utilisateur - BLANC */
    .stChatMessage[data-testid="stChatMessage-user"] p {
        color: #ffffff !important;
        font-size: 0.92rem !important;
        font-weight: 400 !important;
        line-height: 1.8 !important;
        font-style: italic !important;
    }

    /* Texte des réponses - BLANC */
    .stChatMessage[data-testid="stChatMessage-assistant"] p {
        color: #f0f0f5 !important;
        font-size: 0.93rem !important;
        font-weight: 400 !important;
        line-height: 1.8 !important;
    }

    /* Zone de saisie */
    .stChatInput > div {
        border-color: #1b1e30 !important;
        background-color: #0f1422 !important;
        border-radius: 24px !important;
    }
    .stChatInput textarea {
        color: #d0d4e0 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 300 !important;
    }
    .stChatInput textarea::placeholder {
        color: #464a5a !important;
        font-style: italic !important;
    }

    /* Bouton Nouvelle conversation */
    .stButton > button {
        background-color: transparent !important;
        color: #7a8090 !important;
        border: 1px solid #1b1e30 !important;
        border-radius: 20px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 300 !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.06em !important;
        padding: 0.45rem 1.6rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        border-color: #a08230 !important;
        color: #c9a84c !important;
        background-color: transparent !important;
    }

    /* Disclaimer en bas */
    .disclaimer, .disclaimer * {
        text-align: center;
        color: #464a5a !important;
        font-family: 'Inter', sans-serif;
        font-size: 0.62rem;
        font-weight: 200;
        padding: 2rem 1rem 1rem 1rem;
        letter-spacing: 0.04em;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: #1b1e30 !important;
    }

    /* Grille des cartes */
    .pricing-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        padding: 0 0.5rem;
        margin-bottom: 1.5rem;
    }
    @media (max-width: 640px) {
        .pricing-grid {
            grid-template-columns: 1fr;
        }
    }

    /* Cartes de prix */
    .pricing-card {
        border: 1px solid #1b1e30;
        border-radius: 16px;
        padding: 1.5rem 1rem;
        text-align: center;
        background: rgba(15, 20, 34, 0.6);
        transition: border-color 0.3s ease;
        margin-bottom: 0.8rem;
    }
    .pricing-card.populaire {
        border-color: #c9a84c;
    }
    .pricing-badge {
        font-family: 'Inter', sans-serif;
        font-size: 0.58rem;
        font-weight: 400;
        color: #e2c46d;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .pricing-name {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.2rem;
        font-weight: 400;
        color: #e2c46d;
        margin-bottom: 0.3rem;
    }
    .pricing-price {
        font-family: 'Inter', sans-serif;
        font-size: 1.6rem;
        font-weight: 300;
        color: #e8e4e0;
        margin-bottom: 0.2rem;
    }
    .pricing-price span {
        font-size: 0.75rem;
        color: #7a8090;
    }
    .pricing-detail {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 300;
        color: #7a8090;
        margin-bottom: 1rem;
    }
    .pricing-cta {
        display: inline-block;
        padding: 0.6rem 2rem;
        background: linear-gradient(135deg, #c9a84c, #a08230);
        border: none;
        border-radius: 20px;
        color: #0a0e1a;
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.06em;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 12px rgba(201, 168, 76, 0.3);
        cursor: pointer;
    }
    .pricing-cta:hover {
        background: linear-gradient(135deg, #d4b55a, #b0923a);
        box-shadow: 0 4px 20px rgba(201, 168, 76, 0.5);
    }

    /* Paywall header */
    .paywall-header {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 1rem;
    }
    .paywall-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.5rem;
        font-weight: 300;
        color: #e8e4e0;
        margin-bottom: 0.5rem;
    }
    .paywall-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 300;
        color: #7a8090;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Clé API (sécurisée via Streamlit Secrets) ---
CLE_API = st.secrets["ANTHROPIC_API_KEY"]

# --- Prompt système (stocké dans Streamlit Secrets pour protéger le contenu) ---
PROMPT_SYSTEME = st.secrets["PROMPT_SYSTEME"]

MESSAGE_ACCUEIL = "Bienvenue. Ici, pas de conseils, pas de solutions, pas de formules magiques. Juste un espace pour regarder en toi avec honnêteté. Tout ce que tu vis à l'extérieur te parle de ce que tu portes à l'intérieur. Si tu es prêt(e) à regarder, on y va. Qu'est-ce qui t'amène aujourd'hui ?"

# --- En-tête ---
st.markdown("""
<div class="header-container">
    <div class="header-title">Miroir Intérieur</div>
    <div class="header-line"></div>
    <div class="header-sub">Un espace pour voir ce que tu ne regardes pas encore</div>
</div>
""", unsafe_allow_html=True)

# --- Nombre de questions gratuites ---
QUESTIONS_GRATUITES = 2
SEUIL_RESUME = 12       # Nombre de messages avant déclenchement du résumé glissant
NB_MESSAGES_RECENTS = 4  # Nombre de messages récents gardés après résumé
LIMITE_SESSION = 50      # Maximum de messages par session (sécurité anti-abus)

# --- Liens de paiement Stripe ---
LIENS_STRIPE = {
    "Essentiel": {
        "prix": "4,90",
        "detail": "5 échanges / jour",
        "url": "https://buy.stripe.com/dRm4gA1sP05Bh0F3SAbMQ0R"
    },
    "Liberté": {
        "prix": "9,90",
        "detail": "15 échanges / jour",
        "url": "https://buy.stripe.com/8x2cN63AXf0v1lH0GobMQ0S"
    },
    "Premium": {
        "prix": "19,90",
        "detail": "25 échanges / jour",
        "url": "https://buy.stripe.com/14AaEYefB9GbaCh20wbMQ0T",
        "populaire": True
    },
    "Illimité": {
        "prix": "39,90",
        "detail": "Sans aucune limite",
        "url": "https://buy.stripe.com/00waEY2wTf0v25L0GobMQ0U"
    }
}


# --- Fonction de résumé glissant ---
def generer_resume(messages, cle_api):
    """Condense l'historique en notes de séance pour limiter les tokens."""
    client = anthropic.Anthropic(api_key=cle_api)
    conversation = "\n".join([
        f"{'Personne' if m['role'] == 'user' else 'Miroir'}: {m['content']}"
        for m in messages
    ])
    reponse = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=(
            "Résume cette conversation de réflexion intérieure en notes concises. "
            "Capture : les thèmes explorés, les émotions exprimées, les prises de "
            "conscience, les métaphores utilisées, les questions restées ouvertes, "
            "et tout détail important sur la situation de la personne. "
            "Maximum 200 mots. Sois factuel et précis."
        ),
        messages=[{"role": "user", "content": conversation}]
    )
    return reponse.content[0].text


# --- Initialisation de la session ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": MESSAGE_ACCUEIL
    })
if "nb_questions" not in st.session_state:
    st.session_state.nb_questions = 0
if "resume_seance" not in st.session_state:
    st.session_state.resume_seance = ""

# --- Bouton nouvelle conversation ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": MESSAGE_ACCUEIL
        }]
        st.session_state.resume_seance = ""
        st.rerun()

# --- Affichage des messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Saisie utilisateur ou Paywall ---
if st.session_state.nb_questions >= QUESTIONS_GRATUITES:
    # Paywall : afficher les offres d'abonnement
    st.markdown("""
    <div class="paywall-header">
        <div style="width: 50px; height: 1px; background: linear-gradient(90deg, transparent, #e2c46d, transparent); margin: 0 auto 1.5rem auto;"></div>
        <div class="paywall-title">Ce premier échange t'a parlé ?</div>
        <div class="paywall-sub">Continue à explorer ton intérieur avec un accès complet.</div>
    </div>
    """, unsafe_allow_html=True)

    # Construire les cartes dans un composant HTML natif (iframe, pas de sanitisation Streamlit)
    cartes_html = ""
    for nom, info in LIENS_STRIPE.items():
        est_populaire = info.get("populaire", False)
        border_style = "border-color: #c9a84c;" if est_populaire else ""
        badge = '<div style="font-family: Inter, sans-serif; font-size: 0.58rem; color: #e2c46d; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">&#10022; Le plus choisi</div>' if est_populaire else ""
        cartes_html += f"""
        <div style="border: 1px solid #1b1e30; border-radius: 16px; padding: 1.5rem 1rem; text-align: center; background: rgba(15, 20, 34, 0.6); {border_style}">
            {badge}
            <div style="font-family: Cormorant Garamond, Georgia, serif; font-size: 1.2rem; color: #e2c46d; margin-bottom: 0.3rem;">{nom}</div>
            <div style="font-family: Inter, sans-serif; font-size: 1.6rem; font-weight: 300; color: #e8e4e0; margin-bottom: 0.2rem;">{info['prix']}&#8364;<span style="font-size: 0.75rem; color: #7a8090;">/mois</span></div>
            <div style="font-family: Inter, sans-serif; font-size: 0.7rem; color: #7a8090; margin-bottom: 1rem;">{info['detail']}</div>
            <a href="{info['url']}" target="_blank" rel="noopener noreferrer" style="display: inline-block; padding: 0.6rem 2rem; background: linear-gradient(135deg, #c9a84c, #a08230); border-radius: 20px; color: #0a0e1a; font-family: Inter, sans-serif; font-size: 0.8rem; font-weight: 500; text-decoration: none; box-shadow: 0 2px 12px rgba(201, 168, 76, 0.3);">Commencer</a>
        </div>"""

    html_complet = f"""
    <html><body style="margin:0; padding:0; background:transparent; font-family: Inter, sans-serif;">
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; padding: 0.5rem;">
        {cartes_html}
    </div>
    </body></html>
    """
    st.components.v1.html(html_complet, height=420)

else:
    # Question gratuite disponible
    restantes = QUESTIONS_GRATUITES - st.session_state.nb_questions
    if restantes > 0:
        if restantes == QUESTIONS_GRATUITES:
            texte_offre = f"&#10022; {restantes} questions offertes pour découvrir Miroir Intérieur"
        else:
            texte_offre = f"&#10022; Dernière question gratuite"
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 0.5rem;">
            <span style="font-family: 'Inter', sans-serif; font-size: 0.68rem; font-weight: 300; color: #c9a84c; letter-spacing: 0.08em;">
                {texte_offre}
            </span>
        </div>
        """, unsafe_allow_html=True)

    if prompt := st.chat_input("Qu'est-ce qui t'amène ?"):
        # Afficher le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Incrémenter le compteur
        st.session_state.nb_questions += 1

        # Appeler l'API avec résumé glissant
        with st.chat_message("assistant"):
            with st.spinner(""):
                try:
                    client = anthropic.Anthropic(api_key=CLE_API)

                    # Construire le prompt système avec notes de séance
                    system_prompt = PROMPT_SYSTEME
                    if st.session_state.resume_seance:
                        system_prompt += (
                            "\n\n## NOTES DE SÉANCE\n\n"
                            "Voici un résumé de ce qui a été exploré précédemment "
                            "dans cette conversation. Utilise ces notes pour assurer "
                            "la continuité sans te répéter :\n\n"
                            + st.session_state.resume_seance
                        )

                    reponse = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1024,
                        system=system_prompt,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                    )
                    texte = reponse.content[0].text
                    st.markdown(texte)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": texte
                    })

                    # Résumé glissant : condenser si trop de messages
                    if len(st.session_state.messages) >= SEUIL_RESUME:
                        try:
                            messages_a_resumer = st.session_state.messages[:-NB_MESSAGES_RECENTS]
                            if st.session_state.resume_seance:
                                messages_a_resumer.insert(0, {
                                    "role": "assistant",
                                    "content": "Résumé précédent : " + st.session_state.resume_seance
                                })
                            st.session_state.resume_seance = generer_resume(
                                messages_a_resumer, CLE_API
                            )
                            st.session_state.messages = st.session_state.messages[-NB_MESSAGES_RECENTS:]
                        except Exception:
                            pass  # En cas d'erreur, garder l'historique complet

                except anthropic.AuthenticationError:
                    st.error("Clé API invalide. Vérifie ta clé Anthropic.")
                except Exception as e:
                    st.error(f"Erreur : {e}")

        # Si c'était la dernière question gratuite, rerun pour afficher le paywall
        if st.session_state.nb_questions >= QUESTIONS_GRATUITES:
            st.rerun()

# --- Disclaimer ---
st.markdown("""
<div class="disclaimer">
    Espace de réflexion, pas un substitut professionnel. Urgence : 3114 (24h/24).
</div>
""", unsafe_allow_html=True)
