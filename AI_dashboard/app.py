# app.py - FIXED VERSION (No Unicode Issues)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sheet_qa import answer_question_from_sheet, fetch_sheet_data, load_model, WEB_APP_URL, MODEL_NAME, test_system
import traceback
import logging
import os


LOG_FILE = 'executive_demo.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Global variables
qa_model = None

def initialize_model():
    """Initialize the AI model"""
    global qa_model
    try:
        logger.info(f"Loading AI model: {MODEL_NAME}")
        qa_model = load_model(MODEL_NAME)
        if qa_model is None:
            logger.error("Model failed to load")
            return False
        else:
            logger.info("Model loaded successfully!")
            return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

# Initialize on startup
logger.info("Starting Executive Demo Server...")
model_loaded = initialize_model()

@app.route('/')
def serve_index():
    """Serve the React demo interface"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Executive AI question answering endpoint"""
    try:
        logger.info("Received executive question")
        
        # Validate request
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No JSON data provided"}), 400
        
        question = data.get('question')
        logger.info(f"Question: {question}")

        if not question:
            logger.error("No question provided")
            return jsonify({"error": "No question provided"}), 400

        # Check model status
        if qa_model is None:
            logger.error("AI model not loaded")
            initialize_model()
            if qa_model is None:
                return jsonify({"error": "AI model unavailable. Please contact technical support."}), 500

        # Fetch latest sheet data
        logger.info("Fetching latest Google Sheet data...")
        try:
            current_sheet_data_df = fetch_sheet_data(WEB_APP_URL)
            logger.info(f"Sheet data fetched. Shape: {current_sheet_data_df.shape}")
        except Exception as e:
            logger.error(f"Error fetching sheet data: {str(e)}")
            return jsonify({"error": f"Could not fetch Google Sheet data: {str(e)}"}), 500

        if current_sheet_data_df.empty:
            logger.warning("Sheet data is empty")
            return jsonify({
                "answer": "No data currently available. Please add data to your Google Sheet.",
                "status": "success"
            })

        # Process question with AI
        logger.info("Processing with AI...")
        try:
            answer = answer_question_from_sheet(question, current_sheet_data_df, qa_model)
            logger.info(f"AI response generated")
            
            return jsonify({
                "answer": answer,
                "status": "success",
                "data_rows": len(current_sheet_data_df),
                "columns": list(current_sheet_data_df.columns)
            })
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return jsonify({"error": f"Error processing question: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """System health check for executives"""
    try:
        model_status = "Operational" if qa_model is not None else "Offline"
        url_configured = WEB_APP_URL != "YOUR_DEPLOYED_APPS_SCRIPT_URL_HERE"
        
        return jsonify({
            "status": "Executive Demo System",
            "ai_model": model_status,
            "sheet_connection": "Ready" if url_configured else "Needs Configuration",
            "system_ready": qa_model is not None and url_configured,
            "web_app_url": WEB_APP_URL[:50] + "..." if len(WEB_APP_URL) > 50 else WEB_APP_URL
        })
    except Exception as e:
        return jsonify({"status": "System Error", "error": str(e)}), 500

@app.route('/test-sheet', methods=['GET'])
def test_sheet():
    """Test Google Sheet connection"""
    try:
        logger.info("Testing sheet connection...")
        sheet_data = fetch_sheet_data(WEB_APP_URL)
        return jsonify({
            "status": "success",
            "rows": len(sheet_data),
            "columns": list(sheet_data.columns) if not sheet_data.empty else [],
            "sample_data": sheet_data.head(3).to_dict('records') if not sheet_data.empty else []
        })
    except Exception as e:
        logger.error(f"Error testing sheet: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/demo-status', methods=['GET'])
def demo_status():
    """Demo readiness check"""
    try:
        url_configured = WEB_APP_URL != "YOUR_DEPLOYED_APPS_SCRIPT_URL_HERE"
        demo_ready = qa_model is not None and url_configured
        
        return jsonify({
            "demo_ready": demo_ready,
            "components": {
                "ai_model": qa_model is not None,
                "sheet_connection": url_configured
            },
            "message": "READY FOR EXECUTIVE DEMO" if demo_ready else "Setup incomplete"
        })
    except Exception as e:
        return jsonify({"demo_ready": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("EXECUTIVE DEMO SERVER")
    print("=" * 60)
    print(f"AI Model: {'Loaded' if qa_model else 'Failed'}")
    print(f"Sheet URL: {'Configured' if WEB_APP_URL != 'YOUR_DEPLOYED_APPS_SCRIPT_URL_HERE' else 'Need to update'}")
    print(f"Demo URL: http://localhost:8080")
    print("=" * 60)
    
    if not model_loaded or WEB_APP_URL == "YOUR_DEPLOYED_APPS_SCRIPT_URL_HERE":
        print("SETUP REQUIRED:")
        if WEB_APP_URL == "YOUR_DEPLOYED_APPS_SCRIPT_URL_HERE":
            print("   1. Deploy Google Apps Script")
            print("   2. Update WEB_APP_URL in sheet_qa.py")
        if not model_loaded:
            print("   3. Check internet connection for AI model")
        print("=" * 60)
    
    app.run(debug=True, host='localhost', port=8080)
