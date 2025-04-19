from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.utils.chatbot import get_chatbot_response
from app.models.chat import ChatMessage
from app import db

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/')
@login_required
def index():
    # Get chat history
    chat_history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp).all()
    
    return render_template('chatbot/index.html', chat_history=chat_history)

@chatbot_bp.route('/send', methods=['POST'])
@login_required
def send():
    message = request.form.get('message')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get response from chatbot
    response = get_chatbot_response(message, current_user.id)
    
    return jsonify({
        'user_message': message,
        'bot_response': response
    })
