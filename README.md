# Chilli Leaf Disease Detection Web Application

## 🌶️ Project Overview
A Flask-based web application for detecting diseases in chilli leaves using a trained CNN model. This application provides an intuitive interface for farmers and agricultural professionals to identify chilli plant diseases through image upload.

## 📚 Dataset
Link :- https://www.kaggle.com/datasets/ravindubandara3002/preprocessed-chilli-disease-dataset

## 🎯 Features
- **Real-time Disease Detection**: Upload chilli leaf images and get instant predictions
- **Camera Capture**: Take photos directly from your device camera for analysis
- **Smart Image Validation**: Uses Google Gemini AI to verify that uploaded images are chilli plants
- **5 Disease Classes**: Detects Whitefly, Yellowish, Healthy, Anthracnose, and Leaf Curl Virus
- **Confidence Scores**: Shows prediction confidence and probability distribution
- **Treatment Recommendations**: Provides symptoms and treatment guidelines for each disease
- **User-Friendly Interface**: Clean, responsive design with drag-and-drop upload
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## 📋 Prerequisites
- Python 3.8 or higher
- Trained model file (`.keras`, `.h5`, or SavedModel format)
- `class_names.json` file with disease labels

## 🚀 Installation

### 1. Clone or Navigate to Project Directory
```bash
cd "c:\Users\ASUS\Desktop\Chilli"
```

### 2. Install Required Packages
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask tensorflow keras numpy Pillow Werkzeug
```

## 📁 Project Structure
```
Chilli/
│
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── class_names.json               # Disease class names (auto-generated from notebook)
├── best_chilli_disease_model.h5   # Trained model (from Jupyter notebook)
│
├── templates/
│   ├── index.html                 # Home page
│   └── about.html                 # About page
│
├── static/
│   ├── css/
│   │   └── style.css              # Styling
│   └── uploads/                   # Uploaded images (auto-created)
│
├── train/                         # Training data
├── valid/                         # Validation data
└── test/                          # Test data
```

## 🏃 Running the Application

### 1. Make Sure Model Files Exist
Ensure you have trained the model using the Jupyter notebook and have either:
- `chilli_disease_detection_model_final.keras` (recommended)
- `chilli_disease_detection_model_final.h5`
- `best_chilli_disease_model.h5`

### 2. Set Up Gemini API Key (Required for Image Validation)
The application uses Google's Gemini AI to validate that uploaded images are chilli plants.

1. Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root (or copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
3. Add your API key to the `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

**Note**: If you skip this step, the validation will be disabled and all images will be allowed through.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Flask (Web framework)
- TensorFlow/Keras (Deep learning)
- google-generativeai (Gemini API)
- Pillow (Image processing)
- And other dependencies

### 4. Start the Flask Server
```bash
python app.py
```

Or on Windows:
```bash
set FLASK_APP=app.py
set GEMINI_API_KEY=your_api_key_here
python app.py
```

On Linux/Mac:
```bash
export FLASK_APP=app.py
export GEMINI_API_KEY=your_api_key_here
python app.py
```

### 5. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

Or from another device on the same network:
```
http://YOUR_IP_ADDRESS:5000
```

## 📱 How to Use

1. **Upload Image**: 
   - Click "Choose Image" or drag and drop a chilli leaf image
   - OR click "Open Camera" to capture a photo directly
   - Supported formats: PNG, JPG, JPEG

2. **Automatic Validation**:
   - The system uses AI to verify the image contains a chilli plant
   - If it's not a chilli plant, you'll receive a clear error message
   - This prevents false diagnoses from wrong plant types

3. **Analyze**: 
   - Click "Analyze Disease" button
   - Wait for the AI model to process the image

4. **View Results**:
   - See the detected disease name
   - Check the confidence score
   - Review probability distribution for all classes
   - Read disease information, symptoms, and treatment recommendations

4. **Analyze More**: 
   - Click "Analyze Another Image" to test more images

## 🔧 Configuration

### Change Port
Edit `app.py` line 316:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port number here
```

### Change Upload Size Limit
Edit `app.py` line 16:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB (change as needed)
```

### Model Selection
The app automatically tries to load models in this order:
1. `chilli_disease_detection_model_final.keras`
2. `chilli_disease_detection_model_final.h5`
3. `best_chilli_disease_model.h5`

## 🧪 API Endpoints

### Health Check
```bash
GET /health
```
Returns model loading status and class count.

### Predict Disease
```bash
POST /predict
Content-Type: multipart/form-data
Body: file=<image_file>
```
Returns JSON with prediction results.

## 🐛 Troubleshooting

### Model Not Found Error
- Run the Jupyter notebook to train and save the model first
- Ensure model files are in the same directory as `app.py`

### Import Errors
```bash
pip install --upgrade tensorflow keras flask
```

### Permission Errors
- Ensure write permissions for `static/uploads` directory
- Run: `mkdir static/uploads` if it doesn't exist

### Port Already in Use
- Change the port in `app.py` or kill the process using the port

## 📊 Disease Classes

1. **Chilli Whitefly** - Insect infestation
2. **Chilli Yellowish** - Nutrient deficiency
3. **Chilli Healthy** - Normal plant
4. **Chilli Anthracnose** - Fungal disease
5. **Chilli Leaf Curl Virus** - Viral disease

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Deep Learning**: TensorFlow, Keras
- **Frontend**: HTML5, CSS3, JavaScript
- **Image Processing**: PIL, NumPy
- **Model**: Custom CNN with 4 convolutional blocks

## 📈 Future Enhancements

- [ ] Add user authentication
- [ ] Save detection history
- [ ] Batch image processing
- [ ] Mobile app version
- [ ] Real-time camera detection
- [ ] Multi-language support
- [ ] Export reports as PDF

## 👨‍💻 Development Mode

To run in development mode with auto-reload:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

For production, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📄 License
This is a final year project for educational purposes.

## 🤝 Support
For issues or questions, please refer to the project documentation or contact your project supervisor.

## 🎓 Credits
Final Year Project - Chilli Leaf Disease Detection System
Powered by TensorFlow, Keras, and Flask
