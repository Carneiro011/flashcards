# app/controllers/flashcard_controller.py

from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.text_processor import TextProcessor

flashcard_bp = Blueprint("flashcard", __name__, url_prefix="")


@flashcard_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@flashcard_bp.route("/api/status", methods=["GET"])
def status():
    use_ai_config  = current_app.config.get("USE_AI", False)
    gemini_key_raw = current_app.config.get("GEMINI_API_KEY", "")
    key_presente   = bool(gemini_key_raw and gemini_key_raw.strip())

    try:
        import google.generativeai
        gemini_instalado = True
    except ImportError:
        gemini_instalado = False

    return jsonify({
        "USE_AI_no_env":                 use_ai_config,
        "GEMINI_API_KEY_presente":       key_presente,
        "GEMINI_API_KEY_prefixo":        gemini_key_raw[:8] + "..." if key_presente else "VAZIA",
        "google_generativeai_instalado": gemini_instalado,
        "modo_ativo": "ia" if (use_ai_config and key_presente and gemini_instalado) else "regras",
    })


@flashcard_bp.route("/api/gerar", methods=["POST"])
def gerar_flashcards():
    dados = request.get_json()

    texto   = dados.get("texto", "").strip()
    usar_ia = dados.get("usar_ia", False)

    if not texto or len(texto) < 50:
        return jsonify({"erro": "Texto inválido"}), 400

    gemini_key = current_app.config.get("GEMINI_API_KEY", "").strip()
    modo_ia    = usar_ia and bool(gemini_key)

    print(f">>> MODO IA: {modo_ia}")

    try:
        if modo_ia:
            print(">>> IA ativada")
            from app.services.ai_service import AIFlashcardService

            service    = AIFlashcardService()
            flashcards = service.gerar_flashcards(texto)
            modo       = "ia"

        else:
            raise Exception("IA desativada")

    except Exception as e:
        print(f">>> ERRO IA: {e}")
        print(">>> FALLBACK → regras")

        from app.services.text_processor import TextProcessor

        service    = TextProcessor()
        flashcards = service.gerar_flashcards(texto)
        modo       = "regras"

    return jsonify({
        "flashcards": [fc.to_dict() for fc in flashcards],
        "total": len(flashcards),
        "modo": modo
    })