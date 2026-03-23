# 1. IMPORT "flask_mysqldb"
from flask_mysqldb import MySQL
from flask import Flask, jsonify, request, render_template, session, send_from_directory
from flask_cors import CORS 
from werkzeug.security import generate_password_hash, check_password_hash
# 2. IMPORT "MySQLdb" for error handling 
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import os

# --- Configuration ---

app = Flask(__name__, template_folder='.') 
CORS(app) 

# Set a secret key for session management
app.secret_key = 'your_super_secret_key' # IMPORTANT: Change this to a random, secret value

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Your mysql password'  # Your password
app.config['MYSQL_DB'] = 'legalaid_db'

# 3. ADDED: This line makes the cursor return dictionaries (like JSON)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# -----------------------

# --- File Upload Configuration ---
UPLOAD_FOLDER = 'static/uploads/avatars'
CHAT_UPLOAD_FOLDER = 'static/uploads/chat_files' # New folder for chat files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CHAT_UPLOAD_FOLDER'] = CHAT_UPLOAD_FOLDER

# --- Allowed File Extensions ---
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
ALLOWED_CHAT_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx'}

def allowed_avatar(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS

def allowed_chat_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CHAT_EXTENSIONS

def allowed_document(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS
# 4. INITIALIZE "flask_mysqldb"
mysql = MySQL(app)


@app.route('/')
def index():
    """Serves the registration page."""
    return render_template('register.html')

@app.route('/login.html')
def login_page():
    """Serves the login page."""
    return render_template('login.html')

@app.route('/home.html')
def home_page():
    """Serves the home page."""
    return render_template('home.html')

@app.route('/homelogin.html')
def homelogin_page():
    """Serves the logged-in home page."""
    return render_template('homelogin.html')


@app.route('/api/register', methods=['POST'])
def handle_registration():
    """
    API endpoint to handle the multi-step form submission.
    """
    try:
        data = request.get_json()
        print("Received data:", data)

        # --- Step 1: Basic Info ---
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        
        password = data.get('password')
        if not password:
            return jsonify({"error": "Password is required"}), 400
        password_hash = generate_password_hash(password)

        # --- Step 2: Role Details ---
        role = data.get('role')
        if not role:
            return jsonify({"error": "Role is required"}), 400

        location = data.get('location', None)
        language = data.get('language', None)
        case_type = data.get('case_type', None)
        bar_id = data.get('bar_id', None)
        
        # Convert empty string for experience to None (NULL in DB)
        experience_str = data.get('experience', '')
        experience = int(experience_str) if experience_str.isdigit() else None

        specialization = data.get('specialization', None)
        documents = data.get('documents', None) 

        # --- Step 3: Security & Finish ---
        enable_2fa = data.get('2fa', False) 
        how_did_you_hear = data.get('how_did_you_hear', None)
        
        
        # --- Database Insertion ---
        conn = mysql.connection
        # 5. CURSOR: Now uses the default from app.config
        cursor = conn.cursor()
        
        query = """
        INSERT INTO users (
            first_name, last_name, email, phone, password_hash, role, 
            location, language, case_type, 
            bar_id, experience, specialization, document_path, 
            enable_2fa, how_did_you_hear
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s
        )
        """
        
        params = (
            first_name, last_name, email, phone, password_hash, role,
            location, language, case_type,
            bar_id, experience, specialization, documents,
            enable_2fa, how_did_you_hear
        )
        
        cursor.execute(query, params)
        conn.commit()
        
        cursor.close()
        
        return jsonify({"message": "User created successfully!"}), 201

    # 6. ERROR HANDLING: Changed to catch errors from "MySQLdb"
    except (MySQLdb.Error, MySQLdb.Warning) as err:
        # Check the error code
        # err.args[0] is the standard way to get the error number
        if err.args[0] == 1062: # Duplicate entry
            return jsonify({"error": "An account with this email already exists."}), 409
        
        print(f"Database error: {err}")
        return jsonify({"error": "A database error occurred."}), 500
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/api/login', methods=['POST'])
def handle_login():
    """Handles user login."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password_hash'], password):
            # Login successful. In a real app, you'd create a session or JWT here.
            user_data = {
                'id': user['id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email'],
                'role': user['role']
            }
            # Store user data in the session
            session['user'] = user_data
            return jsonify({"message": "Login successful", "user": user_data}), 200
        else:
            # Invalid credentials
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        print(f"An error occurred during login: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/api/profile', methods=['GET', 'POST'])
def handle_profile():
    """Handles fetching and updating a user's profile based on their role."""
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session['user']['id']
    user_role = session['user']['role']
    cursor = mysql.connection.cursor()

    if request.method == 'GET':
        try:
            # This now only fetches generic user info, regardless of role.
            cursor.execute("SELECT first_name, last_name, email, phone, location FROM users WHERE id = %s", (user_id,))
            user_profile = cursor.fetchone()
            if user_profile:
                return jsonify(user_profile), 200
            else:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            print(f"Database error on GET: {e}")
            return jsonify({"error": "Database error occurred"}), 500
        finally:
            cursor.close()

    # The POST method logic for updating lawyer profiles has been removed.
    # If a POST request is sent to this endpoint, Flask will now return a 405 Method Not Allowed error.
    # To handle this more gracefully, you could explicitly return an error:
    return jsonify({"error": "Method not supported"}), 405

@app.route('/api/lawyer/profile', methods=['GET', 'POST'])
def handle_lawyer_profile():
    """
    Handles fetching and updating a lawyer's profile from profile.json.
    """
    PROFILE_FILE = 'profile.json'

    if request.method == 'GET':
        if not os.path.exists(PROFILE_FILE):
            return jsonify({}) # Return empty object if no profile exists
        try:
            with open(PROFILE_FILE, 'r') as f:
                profile_data = json.load(f)
            return jsonify(profile_data)
        except (json.JSONDecodeError, FileNotFoundError):
            return jsonify({})

    if request.method == 'POST':
        try:
            # Load existing data first to preserve fields not in the form (like avatar_url)
            profile_data = {}
            if os.path.exists(PROFILE_FILE):
                with open(PROFILE_FILE, 'r') as f:
                    try:
                        profile_data = json.load(f)
                    except json.JSONDecodeError:
                        pass # File is empty or corrupt, start fresh

            # Since we are handling file uploads, we use request.form for text fields
            # and request.files for the avatar.
            # Update fields from the form, falling back to existing data if a field is not present
            profile_data['full_name'] = request.form.get('full_name', profile_data.get('full_name'))
            profile_data['location'] = request.form.get('location', profile_data.get('location'))
            profile_data['languages'] = request.form.get('languages', profile_data.get('languages'))
            profile_data['experience'] = request.form.get('experience', profile_data.get('experience'))
            profile_data['specialization'] = request.form.get('specialization', profile_data.get('specialization'))
            profile_data['consultation_fee'] = request.form.get('consultation_fee', profile_data.get('consultation_fee'))
            profile_data['availability_status'] = request.form.get('availability_status', profile_data.get('availability_status'))
            profile_data['short_bio'] = request.form.get('short_bio', profile_data.get('short_bio'))
            # Handle checkbox, which is only present in form data if checked
            profile_data['connect_with_clients'] = 'connect_with_clients' in request.form

            # Handle file upload
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_avatar(file.filename):
                    filename = secure_filename(file.filename)
                    # Ensure the upload folder exists
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    profile_data['avatar_url'] = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')

            with open(PROFILE_FILE, 'w') as f:
                json.dump(profile_data, f, indent=4)

            return jsonify({"message": "Profile saved successfully!"}), 200

        except Exception as e:
            print(f"Error saving profile: {e}")
            return jsonify({"error": "An internal server error occurred."}), 500 

@app.route('/api/public/lawyers', methods=['GET'])
def get_public_lawyers():
    """
    Returns a list of lawyer profiles that are marked as visible to clients.
    For now, it only reads from profile.json.
    """
    public_lawyers = []
    PROFILE_FILE = 'profile.json'
    LAWYER_LIST_FILE = 'lawyer.json'

    # 1. Read the single lawyer profile from profile.json
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r') as f:
                profile_data = json.load(f)
            # Only add the lawyer if they have opted to connect with clients
            if profile_data.get('connect_with_clients'):
                # Standardize the keys to match findlawyers.html expectations
                profile_data['name'] = profile_data.get('full_name')
                public_lawyers.append(profile_data)
        except (json.JSONDecodeError, FileNotFoundError):
            pass # Ignore if the file is empty or corrupted

    # 2. Read the list of lawyers from lawyer.json
    if os.path.exists(LAWYER_LIST_FILE):
        try:
            with open(LAWYER_LIST_FILE, 'r') as f:
                lawyer_list = json.load(f)
                public_lawyers.extend(lawyer_list)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    return jsonify(public_lawyers)

@app.route('/api/all-profiles', methods=['GET'])
def get_all_profiles():
    """
    Returns a combined list of all profiles from lawyer.json, profile.json, and userprofile.json.
    This is used by the dashboards to get information for all users.
    """
    all_profiles = []
    
    # File paths
    LAWYER_LIST_FILE = 'lawyer.json'
    LAWYER_PROFILE_FILE = 'profile.json'
    USER_PROFILE_FILE = 'userprofile.json'

    # Read from lawyer.json (list of lawyers)
    if os.path.exists(LAWYER_LIST_FILE):
        try:
            with open(LAWYER_LIST_FILE, 'r') as f:
                all_profiles.extend(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError): pass

    # Read from profile.json (the single lawyer's own profile)
    if os.path.exists(LAWYER_PROFILE_FILE):
        try:
            with open(LAWYER_PROFILE_FILE, 'r', encoding='utf-8') as f:
                all_profiles.extend([json.load(f)]) # Use extend for consistency
        except (json.JSONDecodeError, FileNotFoundError): pass

    # Read from userprofile.json (the client's profile)
    if os.path.exists(USER_PROFILE_FILE):
        try:
            with open(USER_PROFILE_FILE, 'r', encoding='utf-8') as f:
                user_profile = json.load(f)
                # --- FIX: Ensure user profile has a 'full_name' for consistency ---
                if 'full_name' not in user_profile and 'first_name' in user_profile:
                    user_profile['full_name'] = f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip()
                
                all_profiles.append(user_profile)
        except (json.JSONDecodeError, FileNotFoundError): pass

    return jsonify(all_profiles)

@app.route('/api/favorites', methods=['GET', 'POST'])
def handle_favorites():
    """
    Handles fetching and saving favorite lawyers to fav.json.
    """
    FAVORITES_FILE = 'fav.json'

    if request.method == 'POST':
        try:
            favorites_data = request.get_json()
            # Basic validation
            if not isinstance(favorites_data, list):
                return jsonify({"error": "Invalid data format, expected a list."}), 400
            
            with open(FAVORITES_FILE, 'w') as f:
                json.dump(favorites_data, f, indent=4)
            
            return jsonify({"message": "Favorites saved successfully!"}), 200
        except Exception as e:
            print(f"Error saving favorites: {e}")
            return jsonify({"error": "An internal server error occurred."}), 500

    # Default to GET
    if not os.path.exists(FAVORITES_FILE):
        return jsonify([])
    with open(FAVORITES_FILE, 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/user/profile', methods=['GET', 'POST'])
def handle_user_profile():
    """
    Handles fetching and updating a user's profile from userprofile.json.
    """
    PROFILE_FILE = 'userprofile.json'

    if request.method == 'GET':
        if not os.path.exists(PROFILE_FILE):
            return jsonify({}) # Return empty object if no profile exists
        try:
            with open(PROFILE_FILE, 'r') as f:
                profile_data = json.load(f)
            return jsonify(profile_data)
        except (json.JSONDecodeError, FileNotFoundError):
            return jsonify({})

    if request.method == 'POST':
        try:
            # --- FIX: Load existing data first to preserve avatar_url if no new file is uploaded ---
            existing_data = {}
            if os.path.exists(PROFILE_FILE):
                with open(PROFILE_FILE, 'r') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        pass # File is empty or corrupt, start fresh

            profile_data = {
                'full_name': f"{request.form.get('first_name', '')} {request.form.get('last_name', '')}".strip(),
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'phone': request.form.get('phone'),
                'location': request.form.get('location'),
                'language': request.form.get('language'),
                'email': request.form.get('email'),
                'case_type': request.form.get('case_type'),
                # --- FIX: Preserve old avatar_url by default ---
                'avatar_url': existing_data.get('avatar_url') 
            }

            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and allowed_avatar(file.filename):
                    filename = secure_filename(file.filename)
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    profile_data['avatar_url'] = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')

            with open(PROFILE_FILE, 'w') as f:
                json.dump(profile_data, f, indent=4)

            return jsonify({"message": "Profile saved successfully!", "avatar_url": profile_data.get('avatar_url')}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/logout')
def handle_logout():
    """Logs the user out by clearing the session."""
    session.pop('user', None) # Clear the user session
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/chat/history', methods=['GET', 'POST', 'DELETE'])
def handle_chat_history():
    """Handles fetching, saving, and deleting chat history from chat.json."""
    CHAT_HISTORY_FILE = 'chat.json'

    if request.method == 'GET':
        if not os.path.exists(CHAT_HISTORY_FILE):
            return jsonify([])
        try:
            with open(CHAT_HISTORY_FILE, 'r') as f:
                history = json.load(f)
            return jsonify(history)
        except (json.JSONDecodeError, FileNotFoundError):
            return jsonify([])

    elif request.method == 'POST':
        new_history = request.get_json()
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(new_history, f, indent=4)
        return jsonify({"message": "History saved successfully"}), 200

    elif request.method == 'DELETE':
        # Clear the file by writing an empty list
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump([], f, indent=4)
        return jsonify({"message": "History cleared successfully"}), 200

@app.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """Appends a new message to the chat history. Handles both text and file uploads."""
    CHAT_HISTORY_FILE = 'chat.json'
    try:
        sender_name = request.form.get('sender_name')
        sender_avatar_url = request.form.get('sender_avatar_url')
        recipient = request.form.get('recipient')
        text = request.form.get('text', '')

        if not sender_name or not recipient:
            return jsonify({"error": "Sender and recipient are required"}), 400

        new_message = {
            "id": datetime.now().isoformat(),
            "sender": { "name": sender_name, "avatar_url": sender_avatar_url },
            "recipient": recipient,
            "timestamp": datetime.now().isoformat() + 'Z',
            "text": text,
            "fileUrl": None,
            "fileName": None
        }

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_chat_file(file.filename):
                filename = secure_filename(file.filename)
                if not os.path.exists(app.config['CHAT_UPLOAD_FOLDER']):
                    os.makedirs(app.config['CHAT_UPLOAD_FOLDER'])
                filepath = os.path.join(app.config['CHAT_UPLOAD_FOLDER'], filename).replace('\\', '/')
                file.save(filepath)
                new_message['fileUrl'] = filepath
                new_message['fileName'] = filename

        history = []
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                try: history = json.load(f)
                except json.JSONDecodeError: pass
        
        history.append(new_message)
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/edit', methods=['POST'])
def edit_chat_message():
    CHAT_HISTORY_FILE = 'chat.json'
    try:
        data = request.get_json()
        msg_id = data.get('id')
        new_text = data.get('text')
        if not msg_id or not new_text:
            return jsonify({"error": "Message ID and text required"}), 400
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            for msg in history:
                if msg.get('id') == msg_id:
                    msg['text'] = new_text
                    break
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4)
        return jsonify({"message": "Message updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/delete', methods=['POST'])
def delete_chat_message():
    CHAT_HISTORY_FILE = 'chat.json'
    try:
        data = request.get_json()
        msg_id = data.get('id')
        if not msg_id:
            return jsonify({"error": "Message ID required"}), 400
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            history = [msg for msg in history if msg.get('id') != msg_id]
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4)
        return jsonify({"message": "Message deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cases/add', methods=['POST'])
def add_new_case():
    """Handles adding a new case from the user dashboard."""
    CASES_FILE = 'cases.json'
    CASE_UPLOAD_FOLDER = 'static/uploads/cases'
    try:
        # --- Load existing cases ---
        if os.path.exists(CASES_FILE):
            with open(CASES_FILE, 'r') as f:
                try:
                    cases = json.load(f)
                except json.JSONDecodeError:
                    cases = []
        else:
            cases = []

        # --- Handle file uploads ---
        uploaded_files = request.files.getlist('documents')
        document_paths = []
        if uploaded_files:
            if not os.path.exists(CASE_UPLOAD_FOLDER):
                os.makedirs(CASE_UPLOAD_FOLDER)
            
            for file in uploaded_files:
                if file and allowed_document(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(CASE_UPLOAD_FOLDER, filename).replace('\\', '/')
                    file.save(filepath)
                    document_paths.append({"name": filename, "url": filepath})

        # --- Create new case data from form ---
        new_case = {
            "caseId": f"CASE-{len(cases) + 1:03d}",
            "title": request.form.get('case_title'),
            "lawyer": request.form.get('case_lawyer', 'Not Assigned'),
            "description": request.form.get('case_description'),
            "status": request.form.get('status', 'Pending'),
            "nextHearing": request.form.get('nextHearing') or None,
            "lastUpdate": "Case created by user.",
            "documents": document_paths
        }

        # --- Save the new case data to cases.json ---
        cases.append(new_case)
        with open(CASES_FILE, 'w') as f:
            json.dump(cases, f, indent=4)

        return jsonify(new_case), 201 # Return the newly created case
    except Exception as e:
        print(f"Error adding new case: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/api/cases/update', methods=['POST'])
def update_existing_case():
    """Handles updating an existing case."""
    CASES_FILE = 'cases.json'
    CASE_UPLOAD_FOLDER = 'static/uploads/cases'
    try:
        case_id_to_update = request.form.get('caseId')
        if not case_id_to_update:
            return jsonify({"error": "Case ID is missing."}), 400

        # --- Load existing cases ---
        if os.path.exists(CASES_FILE):
            with open(CASES_FILE, 'r') as f:
                cases = json.load(f)
        else:
            return jsonify({"error": "Cases file not found."}), 404

        # --- Find and update the specific case ---
        case_found = False
        for case in cases:
            if case.get('caseId') == case_id_to_update:
                case['title'] = request.form.get('title', case['title'])
                case['description'] = request.form.get('description', case['description'])
                case['status'] = request.form.get('status', case['status'])
                case['nextHearing'] = request.form.get('nextHearing') or case['nextHearing']

                # --- Handle new file uploads and append them ---
                uploaded_files = request.files.getlist('documents')
                if uploaded_files:
                    if not os.path.exists(CASE_UPLOAD_FOLDER):
                        os.makedirs(CASE_UPLOAD_FOLDER)
                    for file in uploaded_files:
                        if file and allowed_document(file.filename):
                            filename = secure_filename(file.filename)
                            filepath = os.path.join(CASE_UPLOAD_FOLDER, filename).replace('\\', '/')
                            file.save(filepath)
                            case['documents'].append({"name": filename, "url": filepath})
                case_found = True
                break
        
        if not case_found:
            return jsonify({"error": f"Case with ID {case_id_to_update} not found."}), 404

        # --- Save the updated list back to cases.json ---
        with open(CASES_FILE, 'w') as f:
            json.dump(cases, f, indent=4)

        return jsonify({"message": "Case updated successfully!"}), 200
    except Exception as e:
        print(f"Error updating case: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/static/uploads/cases/<filename>')
def serve_case_document(filename):
    """Serves an uploaded case document from the correct directory."""
    CASE_UPLOAD_FOLDER = 'static/uploads/cases'
    return send_from_directory(os.path.abspath(CASE_UPLOAD_FOLDER), filename)

@app.route('/api/cases', methods=['GET'])
def get_all_cases():
    """Fetches all cases from cases.json."""
    CASES_FILE = 'cases.json'
    if not os.path.exists(CASES_FILE):
        return jsonify([])
    try:
        with open(CASES_FILE, 'r') as f:
            cases = json.load(f)
        return jsonify(cases)
    except (json.JSONDecodeError, FileNotFoundError):
        return jsonify([])

@app.route('/api/lawyer/cases', methods=['GET', 'POST'])
def handle_lawyer_cases():
    """
    Handles fetching and adding cases for the lawyer's dashboard.
    Uses 'lawyercase.json' for storage.
    """
    LAWYER_CASES_FILE = 'lawyercase.json'
    CASE_UPLOAD_FOLDER = 'static/uploads/cases'

    if request.method == 'GET':
        if not os.path.exists(LAWYER_CASES_FILE):
            return jsonify([])
        try:
            with open(LAWYER_CASES_FILE, 'r') as f:
                cases = json.load(f)
            return jsonify(cases)
        except (json.JSONDecodeError, FileNotFoundError):
            return jsonify([])

    if request.method == 'POST':
        try:
            if os.path.exists(LAWYER_CASES_FILE):
                with open(LAWYER_CASES_FILE, 'r') as f:
                    try:
                        cases = json.load(f)
                    except json.JSONDecodeError:
                        cases = []
            else:
                cases = []

            uploaded_files = request.files.getlist('documents')
            document_paths = []
            if uploaded_files:
                if not os.path.exists(CASE_UPLOAD_FOLDER):
                    os.makedirs(CASE_UPLOAD_FOLDER)
                for file in uploaded_files:
                    if file and allowed_document(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(CASE_UPLOAD_FOLDER, filename).replace('\\', '/')
                        file.save(filepath)
                        document_paths.append({"name": filename, "url": filepath})

            new_case = {
                "caseId": f"LCASE-{len(cases) + 1:03d}",
                "title": request.form.get('case_title'),
                "lawyer": request.form.get('case_lawyer'),
                "description": request.form.get('case_description'),
                "status": request.form.get('status', 'Pending'),
                "nextHearing": request.form.get('nextHearing') or None,
                "documents": document_paths
            }

            cases.append(new_case)
            with open(LAWYER_CASES_FILE, 'w') as f:
                json.dump(cases, f, indent=4)
            return jsonify(new_case), 201
        except Exception as e:
            print(f"Error adding lawyer case: {e}")
            return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)
