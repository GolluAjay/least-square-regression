import pandas as pd
import pyreadstat  # For reading .sav files
from flask_socketio import emit
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

def process_lsr(independent_features,dependent_feature,df) :
        # Ensure selected features exist in the DataFrame
        selected_features = [feature for feature in independent_features if feature in df.columns]
        
        # Handle SVD
        if selected_features:
            A = df[selected_features].to_numpy()
            b = df[dependent_feature].to_numpy()
            # Apply SVD

            # print(np.isnan(A).sum(), "NaN values found")
            # print(np.isinf(A).sum(), "Inf values found")

            A = np.nan_to_num(A, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Check if A is not empty and has at least two dimensions
            if A.size > 0 and A.ndim == 2:
                # Perform SVD
                U, S, Vt = np.linalg.svd(A,full_matrices=0)

                # Calculate the pseudo-inverse of A
                x = Vt.T @ np.linalg.inv(np.diag(S)) @ U.T @ b

                 # Generate the plot
                plt.figure(figsize=(10, 6))
                plt.plot(b, label='Actual Values', color='blue', marker='o')
                plt.plot(A @ x, label='Predicted Values', color='red', marker='x')
                plt.title('Actual vs Predicted Values')
                plt.xlabel('Sample Index')
                plt.ylabel(dependent_feature)
                plt.legend()
                plt.grid(True)

                # Save the plot to a BytesIO object
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                buf.seek(0)

                # Encode the image as base64
                image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                image_data = f"data:image/png;base64,{image_base64}"

                # Emit the image data to the frontend
                emit("plot_image", {"image": image_data})


            else:
                print("Error: The matrix A is empty or not 2-dimensional.")
        else:
            print("No valid independent features selected.")


# Function to load a file into a DataFrame
def file_to_dataframe(file, file_extension):
    """Reads a file from memory based on its extension and converts it to a DataFrame."""
    try:
        if file_extension == 'csv':
            df = pd.read_csv(file)
        elif file_extension == 'xlsx':
            df = pd.read_excel(file)
        elif file_extension == 'sav':
            df, meta = pyreadstat.read_sav(file)  # Meta can also be used for additional information
        elif file_extension == 'datatab':
            df = pd.read_csv(file, delimiter='\t')  # Assuming .datatab is tab-delimited
        else:
            df = pd.DataFrame()  # Empty DataFrame if unsupported
       
        return df
    except Exception as e:
        return pd.DataFrame()  # Return empty DataFrame on error