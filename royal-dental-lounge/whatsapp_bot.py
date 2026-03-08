import os
import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Mock Database (In-Memory dictionary for demo purposes)
# In production, replace this with PyMongo connecting to MongoDB Atlas
user_sessions = {}
appointments_db = []

# State constants
STATE_GREETING = "greeting"
STATE_AWAITING_SERVICE = "awaiting_service"
STATE_AWAITING_DATE = "awaiting_date"
STATE_AWAITING_NAME = "awaiting_name"
STATE_HUMAN_HANDOFF = "human_handoff"

def get_menu_text():
    return (
        "Welcome to *Royal Dental Lounge* 🦷✨\n"
        "Located at MLG Square, NH66.\n\n"
        "How can we help your smile today?\n\n"
        "Reply with a number:\n"
        "1️⃣ Book an Appointment\n"
        "2️⃣ See Services & Pricing Info\n"
        "3️⃣ Clinic Location & Working Hours\n"
        "4️⃣ Speak to to Receptionist"
    )

def handle_booking_flow(sender, body, session):
    state = session.get('state')
    
    if state == STATE_AWAITING_SERVICE:
        services = ["Laser Dentistry", "Implants", "Root Canal", "Cosmetic", "General Checkup"]
        try:
            choice = int(body)
            if 1 <= choice <= 5:
                session['service'] = services[choice-1]
                session['state'] = STATE_AWAITING_DATE
                return f"Great. You selected {session['service']}.\n\nWhen would you like to visit? (e.g., 'Tomorrow morning', 'Friday 5PM')"
            else:
                return "Invalid choice. Please reply with a number from 1 to 5."
        except ValueError:
            return "Please reply with a valid number (1-5)."
            
    elif state == STATE_AWAITING_DATE:
        session['preferred_date'] = body
        session['state'] = STATE_AWAITING_NAME
        return "Noted. Finally, may I know your full name?"
        
    elif state == STATE_AWAITING_NAME:
        session['name'] = body
        
        # Save to mock DB
        appointment = {
            "phone": sender,
            "name": session['name'],
            "service": session['service'],
            "preferred_date": session['preferred_date'],
            "status": "pending_clinic_confirmation"
        }
        appointments_db.append(appointment)
        
        # Reset session
        user_sessions.pop(sender, None)
        
        return (
            f"✅ Thank you, {session['name']}!\n\n"
            f"We have noted your request for {session['service']} on {session['preferred_date']}.\n\n"
            "Our front desk will review this and message you shortly to confirm the exact time slot. Have a great day!"
        )
        
    return get_menu_text()


@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():
    """Endpoint for Twilio WhatsApp Webhook"""
    incoming_msg = request.values.get('Body', '').strip().lower()
    sender = request.values.get('From', '')
    
    # Initialize response
    resp = MessagingResponse()
    msg_reply = resp.message()
    
    # Get or create user session
    if sender not in user_sessions:
        user_sessions[sender] = {'state': STATE_GREETING}
    
    session = user_sessions[sender]
    current_state = session['state']
    
    # Global exit/reset command
    if incoming_msg in ['hi', 'hello', 'menu', 'reset', 'start']:
        user_sessions[sender] = {'state': STATE_GREETING}
        msg_reply.body(get_menu_text())
        return str(resp)

    # Route based on State
    if current_state == STATE_GREETING:
        if incoming_msg == '1':
            session['state'] = STATE_AWAITING_SERVICE
            reply_text = (
                "Let's book your appointment! 📅\n\n"
                "What service are you looking for?\n"
                "1. Laser Dentistry\n"
                "2. Dental Implants\n"
                "3. Root Canal (RCT)\n"
                "4. Cosmetic / Whitening\n"
                "5. General Checkup / Pain"
            )
            msg_reply.body(reply_text)
            
        elif incoming_msg == '2':
            reply_text = (
                "🦷 *Our Premium Services*\n\n"
                "We specialize in pain-free, advanced dentistry.\n"
                "- Laser Dentistry\n"
                "- Dental Implants\n"
                "- Single-sitting RCT\n"
                "- Smile Designing\n\n"
                "For exact pricing, Dr. Litty requires a rapid clinical assessment. "
                "Type *1* to book a consultation, or type *menu* to go back."
            )
            msg_reply.body(reply_text)
            
        elif incoming_msg == '3':
            reply_text = (
                "📍 *Royal Dental Lounge Location*\n"
                "MLG Square, Ground Floor, NH66, Kerala.\n\n"
                "🕒 *Hours*\n"
                "Monday to Sunday: 8:30 AM - 8:30 PM\n\n"
                "🗺️ Google Maps: https://maps.google.com\n\n"
                "Type *menu* to go back."
            )
            msg_reply.body(reply_text)
            
        elif incoming_msg == '4':
            session['state'] = STATE_HUMAN_HANDOFF
            msg_reply.body("I'm transferring you to our human receptionist. They will reply to this chat shortly. Please wait! 🕒")
            
        else:
            msg_reply.body("Sorry, I didn't understand that. " + get_menu_text())
            
    elif current_state in [STATE_AWAITING_SERVICE, STATE_AWAITING_DATE, STATE_AWAITING_NAME]:
        response_text = handle_booking_flow(sender, incoming_msg, session)
        msg_reply.body(response_text)
        
    elif current_state == STATE_HUMAN_HANDOFF:
        # Silently log messages until staff replies (out of scope for basic bot)
        pass 

    return str(resp)


@app.route('/', methods=['GET'])
def health_check():
    return "Royal Dental Lounge AI Bot is running securely. 🚀", 200

if __name__ == '__main__':
    # Run in debug mode for local testing
    app.run(host='0.0.0.0', port=5000, debug=True)
