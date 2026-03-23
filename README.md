# LegalAid AI - Project README

## Overview

LegalAid AI is a web application designed to connect individuals with legal professionals and provide access to legal information. It offers a user-friendly interface with features for registration, login, profile management, direct messaging, and case management. The platform aims to streamline the process of seeking legal assistance and enhance accessibility to justice.

## Key Features

*   **User Authentication:** Secure registration and login functionality for both clients and lawyers.
*   **Profile Management:** Customizable profiles for users and lawyers, allowing them to showcase their information and expertise.
*   **Direct Messaging:** A real-time chat system enabling direct communication between clients and lawyers, including file sharing.
*   **Case Management:** Tools for users and lawyers to add, update, and track legal cases.
*   **Legal Knowledge Base:** A collection of articles and resources covering various areas of law.
*   **Responsive Design:** A user interface that adapts to different screen sizes and devices.
*   **AI Assistant Integration:** Access to an AI assistant for analyzing specific legal situations.

## Project Structure

The project consists of the following main components:

*   **HTML Templates:** Define the structure and layout of the web application's pages.
*   **CSS Styling:** Implemented using Tailwind CSS for a modern and responsive design.
*   **JavaScript Functionality:** Handles user interactions, data fetching, and dynamic content rendering.
*   **Flask Backend:** Provides the server-side logic, API endpoints, and database connectivity.
*   **Database:** MySQL database to store user information, case details, and other relevant data.

## File Manifest

*   `main.py`: Contains the Flask application, API endpoints, and database connection logic.
*   `register.html`: HTML template for the registration page.
*   `login.html`: HTML template for the login page.
*   `home.html`: HTML template for the general home page.
*   `homelogin.html`: HTML template for the logged-in user's home page.
*   `lawyersdashboard.html`: HTML template for the lawyer's dashboard.
*   `userdashboard.html`: HTML template for the user's dashboard.
*   `knowledge-base.html`: HTML template for the legal knowledge base hub.
*   `employment-law.html`, `family-law.html`, `buiseness-law.html`, `consumer-law.html`, `motor-law.html`: HTML templates for the legal knowledge base articles.
*   `askai.html`: HTML template for the "Ask AI" page.
*   `static/uploads/avatars/`: Directory to store user avatar images.
*   `static/uploads/chat_files/`: Directory to store files shared in the chat.
*   `static/uploads/cases/`: Directory to store documents related to legal cases.
*   `chat.json`: JSON file to store chat history.
*   `cases.json`: JSON file to store user case data.
*   `lawyercase.json`: JSON file to store lawyer case data.
*   `profile.json`: JSON file to store lawyer profile data.
*   `userprofile.json`: JSON file to store user profile data.
*   `fav.json`: JSON file to store favourite lawyers data.

## Setup Instructions

1.  **Install Dependencies:**

    *   Python 3.6+
    *   Flask
    *   Flask-MySQLdb
    *   Werkzeug
    *   Tailwind CSS
    *   Font Awesome

    Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

    Install the required Python packages:
    ```bash
    pip install Flask Flask-MySQLdb Werkzeug flask-cors
    ```
    Install Tailwind CSS and Font Awesome using CDNs, included in the HTML files.
2.  **Configure MySQL Database:**

    *   Install MySQL server.
    *   Create a database named `legalaid_db`.
    *   Update the database configuration in `main.py` with your MySQL credentials:

        ```python
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'your_password'
        app.config['MYSQL_DB'] = 'legalaid_db'
        ```
    *   Create a `users` table with the following structure:

        ```sql
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20),
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('client', 'lawyer') NOT NULL,
            location VARCHAR(255),
            language VARCHAR(50),
            case_type VARCHAR(100),
            bar_id VARCHAR(50),
            experience INT,
            specialization VARCHAR(255),
            document_path VARCHAR(255),
            enable_2fa BOOLEAN DEFAULT FALSE,
            how_did_you_hear VARCHAR(255)
        );
        ```
3.  **Run the Application:**

    ```bash
    python main.py
    ```

    The application will start on `http://127.0.0.1:5000`.

## API Endpoints

*   `POST /api/register`: Registers a new user.
*   `POST /api/login`: Logs in an existing user.
*   `GET /api/profile`: Retrieves user profile information.
*   `POST /api/lawyer/profile`: Updates a lawyer's profile.
*   `GET /api/public/lawyers`: Retrieves a list of public lawyer profiles.
*   `GET /api/all-profiles`: Retrieves a combined list of all profiles.
*   `GET /api/favorites`: Retrieves a user's favorite lawyers.
*   `POST /api/favorites`: Saves a user's favorite lawyers.
*   `GET /api/user/profile`: Retrieves a user's profile.
*   `POST /api/user/profile`: Updates a user's profile.
*   `GET /api/logout`: Logs out the current user.
*   `GET /api/chat/history`: Retrieves chat history.
*   `POST /api/chat/send`: Sends a new chat message.
*   `POST /api/chat/edit`: Edits a chat message.
*   `POST /api/chat/delete`: Deletes a chat message.
*   `POST /api/cases/add`: Adds a new legal case.
*   `POST /api/cases/update`: Updates an existing legal case.
*   `GET /api/cases`: Retrieves all legal cases.
*   `GET /api/lawyer/cases`: Retrieves cases for a specific lawyer.
*    `POST /api/lawyer/cases`: Adds cases for a specific lawyer.

## Technologies Used

*   Flask: Python web framework
*   MySQL: Database management system
*   Tailwind CSS: CSS framework for styling
*   Font Awesome: Icon library
*   Three.js: JavaScript library for creating 3D computer graphics
*   HTML/CSS/JavaScript: Core web technologies

## Contributing

Feel free to contribute to the project by submitting pull requests, reporting issues, or suggesting new features.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Team

*   Yogesh Naik
