from flask import Flask, request, render_template_string, send_from_directory
import math
import re

app = Flask(__name__)

COMMENT_RULES = [
    {
        "pattern": r"\\d{4}",  # Match une année ou une date (4 chiffres)
        "jeanmichel": "J'espère que c'est ton anniversaire ! Sinon, ce sera le mien !",
        "advice": "Évitez d’utiliser des dates. Les attaquants les testent en priorité."
    },
    {
        "pattern": r"(12345|abcdef)",  # Match des séquences simples
        "jeanmichel": "Mais fais un effort, vindiou ! Même ma chaise pourrait deviner ça !",
        "advice": "Utilisez une combinaison plus aléatoire. Les séquences sont trop faciles à deviner."
    },
    {
    "pattern": r"azerty",  # Mot de passe contenant 'azerty'
    "jeanmichel": "Oh frérot, tu t'es cru dans League of Legends ou bien ?",
    "advice": "Évitez d'utiliser des mots évidents comme 'azerty'."
    },

    {
        "pattern": r"\\b(prénom|nom)\\b",  # Exemple de mot commun à personnaliser
        "jeanmichel": "Oh, c'est mignon... mais pas sécurisé du tout !",
        "advice": "Évitez les informations personnelles ou les mots communs."
    }
]

def brute_force_time(password: str, attempts_per_second: int = 1_000_000_000):
    char_space = 0
    if any(c.islower() for c in password):
        char_space += 26
    if any(c.isupper() for c in password):
        char_space += 26
    if any(c.isdigit() for c in password):
        char_space += 10
    if any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?~" for c in password):
        char_space += 32

    total_combinations = char_space ** len(password)
    time_seconds = total_combinations / attempts_per_second
    return {"seconds": time_seconds}

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f} secondes"
    elif seconds < 3600:
        return f"{seconds / 60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds / 3600:.2f} heures"
    elif seconds < 31536000:
        return f"{seconds / 86400:.2f} jours"
    else:
        return f"{seconds / 31536000:.2f} années"

def analyze_password(password):
    feedback = []
    result = brute_force_time(password)
    time_readable = format_time(result['seconds'])
    for rule in COMMENT_RULES:
        if re.search(rule["pattern"], password, re.IGNORECASE):
            feedback.append({
                "jeanmichel": f"{rule['jeanmichel']} (Temps estimé : {time_readable})",
                "advice": rule["advice"]
            })
    if not feedback:
        feedback.append({
            "jeanmichel": f"Pas mal... mais peut-être que tu peux le rendre encore plus solide ! (Temps estimé : {time_readable})",
            "advice": "Utilisez au moins 12 caractères, avec des majuscules, des chiffres et des symboles pour plus de sécurité."
        })
    return feedback

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/', methods=['GET', 'POST'])
def home():
    feedback = None
    jeanmichel_comments = []
    recommendations = []
    show_recommendation_button = False
    img_path = "/static/bandit_1.png"  # Chemin par défaut de l'image de JeanMichel

    if request.method == 'POST':
        password = request.form.get('password', '')
        if not password:
            feedback = ""
        elif len(password) > 128:
            feedback = ""
        elif len(password) < 5:
            feedback = ""
            img_path = "/static/bandit_ez.png"
        elif len(password) > 12 and any(char.isupper() for char in password) and any(char.isdigit() for char in password):
            feedback = ""
            img_path = "/static/bandit_gg.png"
        else:
            feedback = ""

        analysis = analyze_password(password)
        jeanmichel_comments = [a["jeanmichel"] for a in analysis]
        recommendations = [a["advice"] for a in analysis]
        show_recommendation_button = True

    return render_template_string(PAGE_HTML, feedback=feedback, jeanmichel=jeanmichel_comments, advice=recommendations, show_recommendation_button=show_recommendation_button, img_path=img_path)

PAGE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JeanMichel Hacker</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>Bonjour je suis Jean Michel Hacker !</h1>
         <h2>Le gars qui teste ton mot de passe.</h2>
        <div id="jeanmichel">
            <img id="jeanmichel-img" src="{{ img_path }}" alt="JeanMichel">
            <h3 id="jeanmichel-text">"Alors tu penses que t'es solide sur les appuis ?"</h3>
            
        </div>
        <form id="password-form" method="POST" action="/" onsubmit="hideJeanMichelText()">

            <div class="password-container">
                <input type="password" id="password" name="password" placeholder="Votre mot de passe" required>
                <button type="button" class="toggle-visibility" onclick="togglePassword()">👁️</button>
            </div>
            <button type="submit">Tester</button>
        </form>
        <div class="feedback" id="feedback-section">
            {% if feedback %}
                <p>{{ feedback }}</p>
            {% endif %}
            {% if jeanmichel %}
                <ul>
                    {% for comment in jeanmichel %}
                        <li>{{ comment }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
            {% if show_recommendation_button %}
                <button type="button" id="recommendation-btn" onclick="showRecommendation()">Voir la recommandation</button>
            {% endif %}
        </div>
    </div>

    <div class="modal" id="recommendation-modal" style="display: none;">
    <span class="close" onclick="closeModal()">&times;</span>
        <h2>Recommandations pour un mot de passe sûr</h2>
        {% if advice %}
            <ul>
                {% for item in advice %}
                    <li>{{ item }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    </div>

    <script>
    function togglePassword() {
        const passwordInput = document.getElementById('password');
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
    }

    function showRecommendation() {
        document.getElementById('recommendation-modal').style.display = 'block';
    }

    function closeModal() {
        document.getElementById('recommendation-modal').style.display = 'none';
    }

    document.getElementById('password-form').addEventListener('submit', function() {
        document.getElementById('jeanmichel-text').style.display = 'none';
    });
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)

