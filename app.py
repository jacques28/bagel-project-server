from flask import Flask, request, jsonify
from flask_cors import CORS
import bagel
import os
import json
import csv
import io
import traceback

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

client = bagel.Client()
api_key = os.environ.get('BAGEL_API_KEY')
llama3_model_id = "86a1be47-187a-42a5-a1bf-79b190f5b154"  # Replace with actual LLaMA3 model ID
print(f"BAGEL_API_KEY: {api_key}")  # To check if it's None
print(f"LLaMA3 Model ID: {llama3_model_id}")


@app.route('/api/fine-tune', methods=['POST'])
def fine_tune():
    try:
        data = request.json
        asset_id = data.get('assetId')
        user_id = data.get('userId')

        if not asset_id or not user_id:
            return jsonify({"error": "Missing assetId or userId"}), 400

        fine_tune_payload = {
            "title": f"Fine-tuned Bagel Recipe Model - {user_id}",
            "user_id": user_id,
            "asset_id": asset_id,
            "file_name": "dataset.json",  # Assuming the data is stored in this format
            "base_model": llama3_model_id,
            "epochs": 3,
            "learning_rate": 0.01
        }

        print(f"Initiating fine-tuning with payload: {fine_tune_payload}")
        response = client.fine_tune(fine_tune_payload, api_key)
        print(f"Fine-tuning response: {response}")

        return jsonify({"message": "Fine-tuning initiated successfully", "response": response})
    except Exception as e:
        print(f"Error in fine-tuning: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to initiate fine-tuning: {str(e)}"}), 500

# Update the generate_recipe function
@app.route('/api/generate-recipe', methods=['POST'])
def generate_recipe():
    try:
        data = request.json
        inspiration = data.get('inspiration')
        model_id = data.get('modelId', llama3_model_id)  # Use custom model if provided

        if not inspiration:
            return jsonify({"error": "No inspiration provided"}), 400

        generate_payload = {
            "prompt": f"Generate a bagel recipe inspired by: {inspiration}",
            "max_tokens": 500,
            "temperature": 0.7
        }

        print(f"Generating recipe with model ID: {model_id}")
        print(f"Generate payload: {generate_payload}")

        response = client.generate(model_id, generate_payload, api_key)
        print(f"Generation response: {response}")

        if isinstance(response, dict) and 'generated_text' in response:
            generated_recipe = response['generated_text']
        else:
            generated_recipe = "Failed to generate a recipe. Please try again."
            print(f"Unexpected response format: {response}")

        return jsonify({"recipe": generated_recipe})
    except Exception as e:
        print(f"Error generating recipe: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate recipe: {str(e)}"}), 500

# Update the create_dataset function
@app.route('/api/create-dataset', methods=['POST'])
def create_dataset():
    try:
        user_id = request.form['userId']
        file = request.files['file']
        dataset_name = request.form['datasetName']

        asset_payload = {
            "dataset_type": "RAW",
            "title": dataset_name,
            "category": "Bagel Recipes",
            "details": "Dataset for fine-tuning bagel recipe model",
            "tags": ["bagel", "recipe", "dataset"],
            "user_id": user_id
        }

        print(f"Creating asset with payload: {asset_payload}")
        asset = client.create_asset(asset_payload, api_key)
        print(f"Asset creation response: {asset}")

        if isinstance(asset, str):
            asset_id = asset
        elif isinstance(asset, dict) and 'id' in asset:
            asset_id = asset['id']
        else:
            print(f"Unexpected asset response: {asset}")
            return jsonify({"error": "Failed to create asset"}), 500

        # Process the file
        file_content = file.read().decode('utf-8')
        if file.filename.endswith('.json'):
            data = json.loads(file_content)
        elif file.filename.endswith('.csv'):
            data = list(csv.DictReader(io.StringIO(file_content)))
        elif file.filename.endswith('.txt'):
            data = [{'recipe': line.strip()} for line in file_content.splitlines()]
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        print(f"Processed data (first 5 items): {data[:5]}")

        # Upload the data to the asset
        upload_payload = {
            "metadatas": [{"source": "user_upload"} for _ in data],
            "documents": [json.dumps(item) for item in data],
            "ids": [f"recipe_{i}" for i in range(len(data))]
        }

        print(f"Uploading data with payload: {upload_payload}")
        upload_response = client.add_data(asset_id, upload_payload, api_key)
        print(f"Upload response: {upload_response}")

        return jsonify({"message": "Dataset created successfully", "assetId": asset_id})
    except Exception as e:
        print(f"Error creating dataset: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create dataset: {str(e)}"}), 500
    
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
    return jsonify(error=str(e)), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {str(e)}")
    app.logger.error(traceback.format_exc())
    return jsonify(error=str(e), stack_trace=traceback.format_exc()), 500  

@app.route('/api/fine-tune', methods=['POST'])
def fine_tune():
    data = request.json
    asset_id = data['assetId']
    user_id = data['userId']

    response = client.fine_tune(
        title=f"Fine-tuned Bagel Recipe Model - {user_id}",
        user_id=user_id,
        asset_id=asset_id,
        file_name="dataset.json",  # Assuming the data is stored in this format
        base_model=llama3_model_id,
        epochs=3,
        learning_rate=0.01
    )

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)