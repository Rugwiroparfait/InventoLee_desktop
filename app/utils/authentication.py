import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socket
from urllib.parse import urlparse, parse_qs
import gspread
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback from Google"""
    
    def do_GET(self):
        """Process the redirect request from Google OAuth"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Extract the authorization code from the callback URL
        query_components = parse_qs(urlparse(self.path).query)
        
        if 'code' in query_components:
            # Store the authorization code in the server instance
            self.server.auth_code = query_components['code'][0]
            success_message = """
            <html>
            <head><title>InventoLee - Authentication Successful</title></head>
            <style>
              body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #F4F1ED; text-align: center; padding: 50px; }
              .container { background-color: white; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
              h2 { color: #4A6FA5; }
              p { color: #2D3142; line-height: 1.5; }
              .success { color: #508569; font-weight: bold; }
              .close { margin-top: 20px; color: #6B717E; }
            </style>
            <body>
              <div class="container">
                <h2>InventoLee - Google Sheets Authentication</h2>
                <p class="success">✅ Authentication successful!</p>
                <p>Google Sheets access has been granted to InventoLee.</p>
                <p>You can now close this browser window and return to the application.</p>
                <p class="close">This window will close automatically in 5 seconds...</p>
              </div>
              <script>
                setTimeout(function() {
                  window.close();
                }, 5000);
              </script>
            </body>
            </html>
            """
            self.wfile.write(success_message.encode('utf-8'))
        else:
            error_message = """
            <html>
            <head><title>InventoLee - Authentication Failed</title></head>
            <style>
              body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #F4F1ED; text-align: center; padding: 50px; }
              .container { background-color: white; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
              h2 { color: #B95C50; }
              p { color: #2D3142; line-height: 1.5; }
              .error { color: #B95C50; font-weight: bold; }
              .close { margin-top: 20px; color: #6B717E; }
            </style>
            <body>
              <div class="container">
                <h2>InventoLee - Authentication Failed</h2>
                <p class="error">❌ Authentication was not successful.</p>
                <p>Please try again or contact support.</p>
                <p class="close">You can close this browser window.</p>
              </div>
            </body>
            </html>
            """
            self.wfile.write(error_message.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Silence the HTTP server logs"""
        return

class GoogleSheetsAuth:
    """Handle OAuth authentication with Google"""
    
    def __init__(self):
        self.credentials = None
        self.credentials_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'google_token.json'
        )
        self.load_credentials()
    
    def load_credentials(self):
        """Load saved credentials if they exist"""
        if os.path.exists(self.credentials_path):
            try:
                with open(self.credentials_path, 'r') as token:
                    token_info = json.load(token)
                    self.credentials = Credentials.from_authorized_user_info(token_info)
                    
                # Test if credentials are valid and refresh if needed
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh()
                    self.save_credentials()
            except Exception as e:
                print(f"Error loading credentials: {str(e)}")
                self.credentials = None
    
    def save_credentials(self):
        """Save credentials to file"""
        if self.credentials:
            os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
            with open(self.credentials_path, 'w') as token:
                token.write(self.credentials.to_json())
    
    def get_auth_url(self):
        """Generate the authorization URL for Google OAuth"""
        # Create a local web server to receive the callback
        self.server = HTTPServer(('localhost', 0), OAuthCallbackHandler)
        self.server.auth_code = None
        
        # Get the dynamically assigned port
        port = self.server.server_address[1]
        
        # OAuth 2.0 scopes for Google Sheets and Drive
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Get client configuration from file or use client ID and secret directly
        client_config = {
            "installed": {
                "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",  # Replace with your client ID
                "project_id": "inventolee-sheets", 
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",  # Replace with your client secret
                "redirect_uris": [f"http://localhost:{port}"]
            }
        }
        
        # Create the OAuth flow
        flow = Flow.from_client_config(
            client_config,
            scopes,
            redirect_uri=f"http://localhost:{port}"
        )
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store flow for later use in handle_callback
        self.flow = flow
        
        return auth_url, port
    
    def start_auth_server(self, port):
        """Start the local web server in a separate thread"""
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def stop_auth_server(self):
        """Stop the local web server"""
        self.server.shutdown()
        self.server_thread.join()
    
    def handle_callback(self):
        """Process the callback and get credentials"""
        try:
            # Wait for the callback to be processed
            while self.server.auth_code is None:
                # Add a small timeout to avoid high CPU usage
                import time
                time.sleep(0.1)
            
            # Exchange the authorization code for credentials
            self.flow.fetch_token(code=self.server.auth_code)
            self.credentials = self.flow.credentials
            
            # Save the credentials
            self.save_credentials()
            
            return True, "Authentication successful!"
        except Exception as e:
            return False, f"Authentication failed: {str(e)}"
        finally:
            # Always stop the server
            self.stop_auth_server()
    
    def get_gspread_client(self):
        """Get a gspread client using the stored credentials"""
        if not self.credentials:
            return None
        
        return gspread.authorize(self.credentials)
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.credentials is not None
    
    def logout(self):
        """Clear saved credentials"""
        self.credentials = None
        if os.path.exists(self.credentials_path):
            os.remove(self.credentials_path)