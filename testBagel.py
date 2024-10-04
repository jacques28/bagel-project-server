import os
import bagel
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from getpass import getpass
import uuid

title = "newdb " + str(uuid.uuid4())  



load_dotenv()


app = Flask(__name__)


client = bagel.Client()


api_key = os.getenv('BAGEL_API_KEY')
user_id = "104875968884847148312"
if not api_key:
    api_key = getpass("Enter your Bagel API key: ")
    os.environ['BAGEL_API_KEY'] = api_key


@app.route('/')
def index():
    return jsonify({"message": "Bagel API Test Server is running!"})


@app.route('/create-asset', methods=['POST'])
def create_asset():
    try:
        unique_title = "Test Asset " + str(uuid.uuid4())  

        
        payload = {
            "dataset_type": "RAW",  
            "title": unique_title,  
            "category": "Testing",
            "details": "This is a test asset for vector dataset.",
            "tags": ["test", "vector", "dataset"],
            "user_id": user_id
        }

        # Create asset using the Bagel client
        response = client.create_asset(payload, api_key)
        print("Response from Bagel:", response)

        if response and 'id' in response:
            return jsonify({
                "message": "Asset created successfully!",
                "asset_id": response['id'],
                "success": True
            }), 200
        else:
            return jsonify({
                "message": "Asset creation failed or no valid ID received.",
                "success": False
            }), 400
    except Exception as e:
        return jsonify({
            "message": f"Error creating asset: {str(e)}",
            "success": False
        }), 500


# Fetch Asset by ID Route
@app.route('/fetch-asset/<string:asset_id>', methods=['GET'])
def fetch_asset(asset_id):
    try:
        # Fetch asset details using the Bagel client
        response = client.get_asset_info(asset_id, api_key)
        return jsonify({
            "message": "Asset details fetched successfully.",
            "asset": response,
            "success": True
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"Error fetching asset details: {str(e)}",
            "success": False
        }), 500

# Fetch All Assets for a User
@app.route('/fetch-all-assets', methods=['GET'])
def fetch_all_assets():
    try:
        # Use the correct method to fetch all assets
        response = client.get_asset_info(user_id, api_key)
        return jsonify({
            "message": "All assets fetched successfully.",
            "assets": response,
            "success": True
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"Error fetching all assets: {str(e)}",
            "success": False
        }), 500

# Upload File to Asset
@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        data = request.get_json()
        dataset_id = data.get("dataset_id")
        file_path = data.get("file_path")

        response = client.file_upload(file_path, dataset_id, api_key)
        return jsonify({
            "message": "File uploaded successfully.",
            "upload_response": response,
            "success": True
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"Error uploading file: {str(e)}",
            "success": False
        }), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
