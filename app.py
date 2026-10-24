import streamlit as st
import anthropic
import requests
import urllib.parse
from datetime import datetime, timezone

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
    /* Fond bleu nuit profond avec texture grain */
    .stApp {
        background: linear-gradient(180deg, #020308 0%, #060a14 30%, #0a0e1a 70%, #0d1225 100%);
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse 60% 40% at 50% 18%, rgba(226,196,109,0.03) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-conic-gradient(rgba(200,200,200,0.008) 0% 25%, transparent 0% 50%) 0 0 / 3px 3px;
        pointer-events: none;
        z-index: 0;
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

    /* Messages du chat - bulles séparées */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 0.8rem !important;
        max-width: 78% !important;
    }

    /* Cacher les avatars */
    .stChatMessage [data-testid="stChatMessageAvatarUser"],
    .stChatMessage [data-testid="stChatMessageAvatarAssistant"],
    .stChatMessage [data-testid="chatAvatarIcon-user"],
    .stChatMessage [data-testid="chatAvatarIcon-assistant"],
    .stChatMessage img[alt="user avatar"],
    .stChatMessage img[alt="assistant avatar"],
    .stChatMessage .stAvatar {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
    }
    .stChatMessage .stAvatar svg {
        display: none !important;
    }

    /* Bulles utilisateur — alignées à droite, fond doré */
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]),
    .stChatMessage:has([data-testid="stChatMessageAvatarUser"]),
    .stChatMessage:has(img[alt="user avatar"]) {
        margin-left: auto !important;
        margin-right: 0 !important;
        background: rgba(201, 168, 76, 0.10) !important;
        border: 1px solid rgba(201, 168, 76, 0.15) !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 0.9rem 1.2rem !important;
    }

    /* Bulles assistant — alignées à gauche, fond gris-bleu */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]),
    .stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]),
    .stChatMessage:has(img[alt="assistant avatar"]) {
        margin-right: auto !important;
        margin-left: 0 !important;
        background: rgba(192, 200, 216, 0.06) !important;
        border: 1px solid rgba(192, 200, 216, 0.08) !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 0.9rem 1.2rem !important;
    }

    /* Texte des questions utilisateur — doré pâle */
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) p,
    .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) p,
    .stChatMessage:has(img[alt="user avatar"]) p {
        color: #e8d5a0 !important;
        font-size: 0.88rem !important;
        font-weight: 300 !important;
        line-height: 1.7 !important;
    }

    /* Texte des réponses du miroir — gris bleuté, même police */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) p,
    .stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]) p,
    .stChatMessage:has(img[alt="assistant avatar"]) p {
        color: #d0d4e8 !important;
        font-size: 0.88rem !important;
        font-weight: 300 !important;
        line-height: 1.7 !important;
    }

    /* Zone de saisie — champ crème sur fond sombre */
    .stChatInput > div {
        background-color: #F5F0E8 !important;
        border: none !important;
        border-radius: 24px !important;
    }
    .stChatInput textarea {
        color: #2a2520 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 300 !important;
    }
    .stChatInput textarea::placeholder {
        color: #8a8070 !important;
        font-style: italic !important;
    }

    /* Bouton Nouvelle conversation — discret */
    .stButton > button {
        background-color: transparent !important;
        color: #50546a !important;
        border: 1px solid rgba(27, 30, 48, 0.5) !important;
        border-radius: 20px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 300 !important;
        font-size: 0.65rem !important;
        letter-spacing: 0.06em !important;
        padding: 0.35rem 1.2rem !important;
        transition: all 0.3s ease !important;
        opacity: 0.7 !important;
    }
    .stButton > button:hover {
        border-color: #a08230 !important;
        color: #c9a84c !important;
        background-color: transparent !important;
    }

    /* Message d'accueil — distinct du chat */
    .welcome-message {
        text-align: center;
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 0.95rem;
        font-weight: 300;
        font-style: italic;
        color: #9a9eb0;
        line-height: 2;
        letter-spacing: 0.02em;
        padding: 1.5rem 2rem;
        margin: 0 auto 1rem auto;
        max-width: 520px;
        border-top: 1px solid rgba(226,196,109,0.08);
        border-bottom: 1px solid rgba(226,196,109,0.08);
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

    /* Bande basse — même fond que l'app */
    .stBottom, .stBottom > div, [data-testid="stBottom"] {
        background: transparent !important;
    }

    /* Bouton envoi — doré */
    .stChatInput button, .stChatInput [data-testid="stChatInputSubmitButton"] {
        background-color: #c9a84c !important;
        color: #0a0e1a !important;
        border: none !important;
    }
    .stChatInput button:hover, .stChatInput [data-testid="stChatInputSubmitButton"]:hover {
        background-color: #e2c46d !important;
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
        .welcome-message {
            padding: 1rem 1.2rem;
            font-size: 0.85rem;
            max-width: 100%;
        }
        .header-title {
            font-size: 2rem;
        }
        .stChatMessage {
            max-width: 88% !important;
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

    /* Sidebar Streamlit */
    [data-testid="stSidebar"] {
        background: #060a14 !important;
        border-right: 1px solid rgba(226,196,109,0.08) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span {
        font-family: 'Inter', sans-serif !important;
        color: #9a9eb0 !important;
    }
    .sidebar-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.1rem;
        font-weight: 400;
        color: #e8e4e0;
        letter-spacing: 0.02em;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(226,196,109,0.08);
    }
    .conv-item {
        display: block;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.3rem;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 300;
        color: #7a8090;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        border: 1px solid transparent;
    }
    .conv-item:hover {
        background: rgba(201, 168, 76, 0.06);
        border-color: rgba(201, 168, 76, 0.1);
        color: #c9a84c;
    }
    .conv-item.active {
        background: rgba(201, 168, 76, 0.10);
        border-color: rgba(201, 168, 76, 0.15);
        color: #e2c46d;
    }
    .conv-date {
        font-size: 0.6rem;
        color: #50546a;
        margin-top: 0.15rem;
    }

    /* Barre utilisateur */
    .user-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 1rem;
        padding: 0.5rem 1rem 0 1rem;
    }
    .user-bar .user-name {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 300;
        color: #7a8090;
    }
    .user-bar a {
        font-family: 'Inter', sans-serif;
        font-size: 0.62rem;
        font-weight: 300;
        color: #50546a;
        text-decoration: none;
        letter-spacing: 0.04em;
        transition: color 0.2s;
    }
    .user-bar a:hover {
        color: #c9a84c;
    }
</style>
""", unsafe_allow_html=True)

# --- Secrets ---
CLE_API = st.secrets["ANTHROPIC_API_KEY"]
PROMPT_SYSTEME = st.secrets["PROMPT_SYSTEME"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://conseiller-spirituel.streamlit.app")

MESSAGE_ACCUEIL = "Juste un espace pour regarder en toi avec honnêteté. Tout ce que tu vis à l'extérieur te parle de ce que tu portes à l'intérieur.<br><br>Si tu es prêt(e) à regarder, on y va."

# --- Constantes ---
QUESTIONS_GRATUITES = 5
SEUIL_RESUME = 12
NB_MESSAGES_RECENTS = 4
LIMITE_SESSION = 50

LIENS_STRIPE = {
    "Découverte": {
        "prix": "4,90",
        "detail": "5 échanges / jour",
        "url": "https://buy.stripe.com/dRm4gA1sP05Bh0F3SAbMQ0R"
    },
    "Essentiel": {
        "prix": "9,90",
        "detail": "20 échanges / jour",
        "url": "https://buy.stripe.com/8x2cN63AXf0v1lH0GobMQ0S",
        "populaire": True
    },
    "Illimité": {
        "prix": "19,90",
        "detail": "Sans aucune limite",
        "url": "https://buy.stripe.com/14AaEYefB9GbaCh20wbMQ0T"
    }
}


# ============================================================
# AUTHENTIFICATION GOOGLE VIA SUPABASE
# ============================================================

# --- Initialisation du client Supabase (pour l'auth) ---
try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

# --- État d'authentification ---
for key in ["user", "user_id", "user_name", "access_token", "refresh_token"]:
    if key not in st.session_state:
        st.session_state[key] = None

# --- Déconnexion via URL ---
if st.query_params.get("action") == "logout":
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# --- Callback OAuth Google ---
query_code = st.query_params.get("code")
if query_code and not st.session_state.user:
    try:
        # 1) Échanger le code Google contre des tokens
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": query_code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        tokens = token_resp.json()

        if "id_token" in tokens and supabase:
            # 2) Connecter / créer l'utilisateur Supabase avec le token Google
            auth_response = supabase.auth.sign_in_with_id_token({
                "provider": "google",
                "token": tokens["id_token"],
            })

            st.session_state.user = auth_response.user
            st.session_state.user_id = str(auth_response.user.id)
            meta = auth_response.user.user_metadata or {}
            st.session_state.user_name = (
                meta.get("full_name")
                or meta.get("name")
                or (auth_response.user.email or "").split("@")[0]
                or "Utilisateur"
            )
            st.session_state.access_token = auth_response.session.access_token
            st.session_state.refresh_token = auth_response.session.refresh_token

        elif "error" in tokens:
            st.error(
                f"Erreur Google : {tokens.get('error_description', tokens['error'])}"
            )

        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        st.query_params.clear()

# --- Rafraîchir le token Supabase si nécessaire ---
if st.session_state.access_token and supabase:
    try:
        refreshed = supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token,
        )
        if refreshed and refreshed.session:
            st.session_state.access_token = refreshed.session.access_token
            st.session_state.refresh_token = refreshed.session.refresh_token
    except Exception:
        # Token expiré, forcer reconnexion
        st.session_state.user = None
        st.session_state.access_token = None

# --- Page de connexion ---
if not st.session_state.user:
    # En-tête
    st.markdown("""
    <div class="header-container">
        <div class="header-title">Miroir Intérieur</div>
        <div class="header-line"></div>
        <div class="header-sub">Un espace pour voir ce que tu ne regardes pas encore</div>
    </div>
    """, unsafe_allow_html=True)

    # URL d'authentification Google
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "prompt": "select_account",
        })
    )

    # Carte de connexion élégante
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1rem 4rem 1rem;">
        <div style="max-width: 380px; margin: 0 auto; padding: 2.5rem 2rem; border: 1px solid rgba(226,196,109,0.12); border-radius: 20px; background: rgba(15, 20, 34, 0.5);">
            <p style="font-family: 'Inter', sans-serif; font-size: 0.85rem; font-weight: 300; color: #9a9eb0; margin-bottom: 2rem; line-height: 1.7;">
                Connecte-toi pour retrouver tes conversations<br>et avancer à ton rythme.
            </p>
            <a href="{google_auth_url}" style="display: inline-flex; align-items: center; gap: 0.6rem; padding: 0.75rem 2rem; background: #ffffff; border-radius: 24px; color: #3c4043; font-family: 'Inter', sans-serif; font-size: 0.85rem; font-weight: 500; text-decoration: none; box-shadow: 0 1px 3px rgba(0,0,0,0.3); transition: box-shadow 0.2s ease;">
                <svg width="18" height="18" viewBox="0 0 18 18"><path fill="#4285F4" d="M16.51 8H8.98v3h4.3c-.18 1-.74 1.48-1.6 2.04v2.01h2.6a7.8 7.8 0 0 0 2.38-5.88c0-.57-.05-.66-.15-1.18Z"/><path fill="#34A853" d="M8.98 17c2.16 0 3.97-.72 5.3-1.94l-2.6-2a4.8 4.8 0 0 1-7.18-2.54H1.83v2.07A8 8 0 0 0 8.98 17Z"/><path fill="#FBBC05" d="M4.5 10.52a4.8 4.8 0 0 1 0-3.04V5.41H1.83a8 8 0 0 0 0 7.18l2.67-2.07Z"/><path fill="#EA4335" d="M8.98 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59A8 8 0 0 0 1.83 5.41L4.5 7.48a4.77 4.77 0 0 1 4.48-3.9Z"/></svg>
                Continuer avec Google
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        Espace de réflexion, pas un substitut professionnel. Urgence : 3114 (24h/24).
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ============================================================
# UTILISATEUR CONNECTÉ — FONCTIONS BASE DE DONNÉES
# ============================================================

def _db_headers():
    """En-têtes HTTP pour les requêtes Supabase REST API avec auth utilisateur."""
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def charger_conversations():
    """Charge la liste des conversations de l'utilisateur (les plus récentes d'abord)."""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/conversations"
            f"?user_id=eq.{st.session_state.user_id}"
            f"&order=updated_at.desc&limit=20",
            headers=_db_headers(),
            timeout=8,
        )
        return r.json() if r.ok else []
    except Exception:
        return []


def creer_conversation(titre="Nouvelle conversation"):
    """Crée une nouvelle conversation en base."""
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/conversations",
            headers=_db_headers(),
            json={"user_id": st.session_state.user_id, "title": titre},
            timeout=8,
        )
        data = r.json()
        return data[0] if r.ok and data else None
    except Exception:
        return None


def charger_messages_db(conversation_id):
    """Charge les messages d'une conversation depuis Supabase."""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/messages"
            f"?conversation_id=eq.{conversation_id}"
            f"&order=created_at.asc",
            headers=_db_headers(),
            timeout=8,
        )
        return r.json() if r.ok else []
    except Exception:
        return []


def sauvegarder_message(conversation_id, role, content):
    """Sauvegarde un message et met à jour le timestamp de la conversation."""
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/messages",
            headers=_db_headers(),
            json={
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            },
            timeout=8,
        )
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/conversations?id=eq.{conversation_id}",
            headers=_db_headers(),
            json={"updated_at": datetime.now(timezone.utc).isoformat()},
            timeout=8,
        )
    except Exception:
        pass  # Best effort — ne pas bloquer le chat si la sauvegarde échoue


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
        messages=[{"role": "user", "content": conversation}],
    )
    return reponse.content[0].text


# ============================================================
# INITIALISATION DE LA CONVERSATION
# ============================================================

if "conversation_id" not in st.session_state:
    convs = charger_conversations()

    if convs:
        # Reprendre la dernière conversation
        conv = convs[0]
        st.session_state.conversation_id = conv["id"]
        msgs_db = charger_messages_db(conv["id"])

        if msgs_db:
            # Reconstruire l'historique : accueil + messages sauvegardés
            st.session_state.messages = [
                {"role": "assistant", "content": MESSAGE_ACCUEIL}
            ]
            st.session_state.messages.extend(
                [{"role": m["role"], "content": m["content"]} for m in msgs_db]
            )
            st.session_state.nb_questions = sum(
                1 for m in msgs_db if m["role"] == "user"
            )
        else:
            st.session_state.messages = [
                {"role": "assistant", "content": MESSAGE_ACCUEIL}
            ]
            st.session_state.nb_questions = 0
    else:
        # Première utilisation — créer une conversation
        conv = creer_conversation("Première conversation")
        st.session_state.conversation_id = conv["id"] if conv else None
        st.session_state.messages = [
            {"role": "assistant", "content": MESSAGE_ACCUEIL}
        ]
        st.session_state.nb_questions = 0

    st.session_state.resume_seance = ""

if "nb_questions" not in st.session_state:
    st.session_state.nb_questions = 0
if "resume_seance" not in st.session_state:
    st.session_state.resume_seance = ""


# ============================================================
# SIDEBAR — CONVERSATIONS PASSÉES
# ============================================================

with st.sidebar:
    st.markdown('<div class="sidebar-title">Tes conversations</div>', unsafe_allow_html=True)

    # Bouton nouvelle conversation dans la sidebar
    if st.button("+ Nouvelle conversation", use_container_width=True, key="sidebar_new"):
        conv = creer_conversation()
        if conv:
            st.session_state.conversation_id = conv["id"]
        st.session_state.messages = [{"role": "assistant", "content": MESSAGE_ACCUEIL}]
        st.session_state.nb_questions = 0
        st.session_state.resume_seance = ""
        st.rerun()

    st.markdown("---")

    # Charger et afficher la liste des conversations
    conversations_list = charger_conversations()
    for conv in conversations_list:
        # Déterminer le titre à afficher
        titre = conv.get("title", "Conversation")
        if titre == "Nouvelle conversation" or titre == "Première conversation":
            # Essayer d'utiliser la date comme titre
            date_str = conv.get("created_at", "")
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    titre = dt.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    pass

        # Marquer la conversation active
        is_active = conv["id"] == st.session_state.get("conversation_id")
        css_class = "conv-item active" if is_active else "conv-item"

        # Date de dernière mise à jour
        date_maj = ""
        updated = conv.get("updated_at", "")
        if updated:
            try:
                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                date_maj = dt.strftime("%d/%m à %H:%M")
            except Exception:
                pass

        # Bouton pour charger cette conversation
        if st.button(
            f"{'● ' if is_active else ''}{titre}",
            key=f"conv_{conv['id']}",
            use_container_width=True,
        ):
            if not is_active:
                st.session_state.conversation_id = conv["id"]
                msgs_db = charger_messages_db(conv["id"])
                st.session_state.messages = [
                    {"role": "assistant", "content": MESSAGE_ACCUEIL}
                ]
                if msgs_db:
                    st.session_state.messages.extend(
                        [{"role": m["role"], "content": m["content"]} for m in msgs_db]
                    )
                    st.session_state.nb_questions = sum(
                        1 for m in msgs_db if m["role"] == "user"
                    )
                else:
                    st.session_state.nb_questions = 0
                st.session_state.resume_seance = ""
                st.rerun()

        if date_maj and not is_active:
            st.caption(date_maj)

    # Déconnexion en bas de sidebar
    st.markdown("---")
    st.markdown(
        f'<span style="font-size:0.7rem; color:#7a8090;">{st.session_state.user_name}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<a href="?action=logout" style="font-size:0.65rem; color:#50546a; text-decoration:none;">Se déconnecter</a>',
        unsafe_allow_html=True,
    )


# ============================================================
# INTERFACE PRINCIPALE
# ============================================================

# --- Barre utilisateur (nom + déconnexion) ---
st.markdown(f"""
<div class="user-bar">
    <span class="user-name">{st.session_state.user_name}</span>
    <a href="?action=logout">Se déconnecter</a>
</div>
""", unsafe_allow_html=True)

# --- En-tête ---
st.markdown("""
<div class="header-container">
    <div class="header-title">Miroir Intérieur</div>
    <div class="header-line"></div>
    <div class="header-sub">Un espace pour voir ce que tu ne regardes pas encore</div>
</div>
""", unsafe_allow_html=True)

# --- Affichage des messages ---
for i, message in enumerate(st.session_state.messages):
    if i == 0 and message["role"] == "assistant":
        st.markdown(
            f'<div class="welcome-message">{message["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Saisie utilisateur ou Paywall ---
if st.session_state.nb_questions >= QUESTIONS_GRATUITES:
    # Paywall
    st.markdown("""
    <div class="paywall-header">
        <div style="width: 50px; height: 1px; background: linear-gradient(90deg, transparent, #e2c46d, transparent); margin: 0 auto 1.5rem auto;"></div>
        <div class="paywall-title">Ce premier échange t'a parlé ?</div>
        <div class="paywall-sub">Continue à explorer ton intérieur avec un accès complet.</div>
    </div>
    """, unsafe_allow_html=True)

    cartes_html = ""
    for nom, info in LIENS_STRIPE.items():
        est_populaire = info.get("populaire", False)
        border_style = "border-color: #c9a84c;" if est_populaire else ""
        badge = (
            '<div style="font-family: Inter, sans-serif; font-size: 0.58rem; '
            'color: #e2c46d; letter-spacing: 0.1em; text-transform: uppercase; '
            'margin-bottom: 0.5rem;">&#10022; Le plus choisi</div>'
            if est_populaire
            else ""
        )
        cartes_html += f"""
        <div style="border: 1px solid #1b1e30; border-radius: 16px; padding: 1.5rem 1rem;
                     text-align: center; background: rgba(15, 20, 34, 0.6); {border_style}">
            {badge}
            <div style="font-family: Cormorant Garamond, Georgia, serif; font-size: 1.2rem;
                        color: #e2c46d; margin-bottom: 0.3rem;">{nom}</div>
            <div style="font-family: Inter, sans-serif; font-size: 1.6rem; font-weight: 300;
                        color: #e8e4e0; margin-bottom: 0.2rem;">
                {info['prix']}&#8364;<span style="font-size: 0.75rem; color: #7a8090;">/mois</span>
            </div>
            <div style="font-family: Inter, sans-serif; font-size: 0.7rem; color: #7a8090;
                        margin-bottom: 1rem;">{info['detail']}</div>
            <a href="{info['url']}" target="_blank" rel="noopener noreferrer"
               style="display: inline-block; padding: 0.6rem 2rem;
                      background: linear-gradient(135deg, #c9a84c, #a08230);
                      border-radius: 20px; color: #0a0e1a; font-family: Inter, sans-serif;
                      font-size: 0.8rem; font-weight: 500; text-decoration: none;
                      box-shadow: 0 2px 12px rgba(201, 168, 76, 0.3);">Commencer</a>
        </div>"""

    html_complet = f"""
    <html><body style="margin:0; padding:0; background:transparent; font-family: Inter, sans-serif;">
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; padding: 0.5rem;">
        {cartes_html}
    </div>
    </body></html>
    """
    st.components.v1.html(html_complet, height=320)

else:
    # Questions gratuites disponibles
    restantes = QUESTIONS_GRATUITES - st.session_state.nb_questions
    if restantes > 0:
        if restantes == 1:
            texte_offre = "&#10022; Dernière question gratuite"
        else:
            texte_offre = f"&#10022; {restantes} questions offertes pour découvrir Miroir Intérieur"
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 0.5rem;">
            <span style="font-family: 'Inter', sans-serif; font-size: 0.68rem;
                         font-weight: 300; color: #c9a84c; letter-spacing: 0.08em;">
                {texte_offre}
            </span>
        </div>
        """, unsafe_allow_html=True)

    if prompt := st.chat_input("Qu'est-ce qui t'amène ?"):
        # Afficher et sauvegarder le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Sauvegarder en base
        if st.session_state.conversation_id:
            sauvegarder_message(st.session_state.conversation_id, "user", prompt)

        # Incrémenter le compteur
        st.session_state.nb_questions += 1

        # Appeler l'API Claude avec résumé glissant
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
                        ],
                    )
                    texte = reponse.content[0].text
                    st.markdown(texte)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": texte,
                    })

                    # Sauvegarder la réponse en base
                    if st.session_state.conversation_id:
                        sauvegarder_message(
                            st.session_state.conversation_id, "assistant", texte
                        )

                    # Résumé glissant
                    if len(st.session_state.messages) >= SEUIL_RESUME:
                        try:
                            messages_a_resumer = st.session_state.messages[
                                :-NB_MESSAGES_RECENTS
                            ]
                            if st.session_state.resume_seance:
                                messages_a_resumer.insert(0, {
                                    "role": "assistant",
                                    "content": (
                                        "Résumé précédent : "
                                        + st.session_state.resume_seance
                                    ),
                                })
                            st.session_state.resume_seance = generer_resume(
                                messages_a_resumer, CLE_API
                            )
                            st.session_state.messages = (
                                st.session_state.messages[-NB_MESSAGES_RECENTS:]
                            )
                        except Exception:
                            pass

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
