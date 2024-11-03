from flask import render_template, Blueprint
import io
from . import socketio
from flask_socketio import emit
from .services import file_to_dataframe, process_lsr


# Create a blueprint for routes
routes = Blueprint('routes', __name__)

# Dictionary to store chunks for each file by file ID
file_chunks = {}

# Dictionary to store DataFrames by file ID
processed_dataframes = {}

@routes.route('/')
def upload_form():
    return render_template('upload.html')

@socketio.on("set_features")
def handle_set_features(data):
    file_id = data['fileId']  # Assume fileId is sent with features
    independent_features = data['independent']
    dependent_feature = data['dependent']
    df = processed_dataframes[file_id]
    if file_id in processed_dataframes:
        process_lsr(independent_features,dependent_feature,df)
    else:
        print("No DataFrame found for the provided file ID.")

@socketio.on("upload_file_chunk")
def handle_file_chunk(data):
    file_id = data['fileId']
    extension = data['extension']
    chunk = data['chunk']  # This should be binary data
    is_last_chunk = data['isLastChunk']

    try:
        if file_id not in file_chunks:
            file_chunks[file_id] = io.BytesIO()  # Use BytesIO to hold file data in memory

        # Write the chunk to the BytesIO buffer
        file_chunks[file_id].write(chunk)

        if is_last_chunk:
            # Process the complete file in memory
            file_chunks[file_id].seek(0)  # Move to the beginning of the BytesIO buffer
            file_data = file_chunks[file_id]  # Get the complete data

            # Attempt to convert the file to a DataFrame
            df_data = file_to_dataframe(file_data, extension)

            if df_data is not None:
                 # Store the new DataFrame in the global dictionary
                processed_dataframes[file_id] = df_data

                # If conversion was successful, send success message
                emit("upload_complete", {
                    'status': 'success',
                    "message": "File uploaded and processed successfully!",
                    'keys': list(df_data.keys())
                })
            else:
                # Conversion failed
                emit("upload_complete", {
                    'status': 'error',
                    "message": "Failed to process the file. Unsupported format or read error."
                })

            # Clean up the temporary chunks storage
            del file_chunks[file_id]

    except Exception as e:
        # Handle any unexpected errors and send a failure message
        print(f"Error handling file chunk: {e}")
        if file_id in file_chunks:
            del file_chunks[file_id]  # Clean up any incomplete data
        emit("upload_complete", {
            'status': 'error',
            "message": "An error occurred during file upload or processing."
        })