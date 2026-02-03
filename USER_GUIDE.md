# ChilliDoc AI - User Guide 📖

## Table of Contents
1. [Getting Started](#getting-started)
2. [Using the Web Interface](#using-the-web-interface)
3. [Understanding Results](#understanding-results)
4. [API Usage](#api-usage)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Getting Started

### System Requirements
- **Operating System:** Windows 10+, Linux, macOS
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 2GB free space
- **Browser:** Chrome, Firefox, Safari, Edge (latest versions)
- **Internet:** Required for initial setup

### Quick Start

#### Windows
1. Double-click `start.bat`
2. Wait for installation (first time only)
3. Browser will open automatically at `http://localhost:5000`

#### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

---

## Using the Web Interface

### 1. Upload Image

#### Method A: Drag & Drop
1. Open the application in your browser
2. Drag an image file from your computer
3. Drop it into the upload area
4. Image preview will appear

#### Method B: Click to Browse
1. Click "Select Image" button
2. Choose image from file browser
3. Supported formats: JPG, JPEG, PNG
4. Maximum size: 16MB

### 2. Image Guidelines

✅ **Good Images:**
- Clear, focused photos
- Good lighting (natural daylight preferred)
- Close-up of affected leaves
- Shows disease symptoms clearly
- Minimum 224x224 pixels

❌ **Avoid:**
- Blurry or out-of-focus images
- Too dark or overexposed
- Multiple leaves overlapping
- Extreme angles
- Heavy filters or edits

### 3. Analyze Disease

1. Click "Analyze Disease" button
2. Wait 2-3 seconds for processing
3. Results will appear automatically

---

## Understanding Results

### Disease Information Card

#### 1. Severity Level
- **None** 🟢 - Plant is healthy
- **Medium** 🟡 - Moderate threat, treatable
- **High** 🟠 - Serious condition, immediate action needed
- **Very High** 🔴 - Critical, risk of plant death

#### 2. Confidence Score
- **90-100%** - Very confident prediction
- **80-90%** - High confidence
- **70-80%** - Moderate confidence
- **Below 70%** - Low confidence, consider retaking photo

#### 3. Disease Description
- Overview of the disease
- How it affects plants
- Common triggers

### Treatment Recommendations

#### Conventional Methods
- Chemical fungicides/pesticides
- Application instructions
- Safety precautions
- Frequency of treatment

#### Organic Solutions
- Natural remedies (neem oil, garlic spray)
- Biological controls
- Cultural practices
- Environmentally friendly options

### Prevention Tips
- How to avoid disease recurrence
- Best agricultural practices
- Soil and water management
- Plant spacing and hygiene

---

## API Usage

### Making Predictions

#### Python Example
```python
import requests

# API endpoint
url = "http://localhost:5000/api/predict"

# Open image file
with open("chilli_leaf.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

# Parse results
result = response.json()
print(f"Disease: {result['prediction']['predicted_class']}")
print(f"Confidence: {result['prediction']['confidence']:.2f}%")

# Get treatment info
treatment = result['disease_info']['treatment']
for step in treatment:
    print(f"- {step}")
```

#### JavaScript/Node.js Example
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('chilli_leaf.jpg'));

axios.post('http://localhost:5000/api/predict', form, {
  headers: form.getHeaders()
})
  .then(response => {
    console.log('Disease:', response.data.prediction.predicted_class);
    console.log('Confidence:', response.data.prediction.confidence);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

#### cURL Example
```bash
curl -X POST http://localhost:5000/api/predict \
  -F "file=@chilli_leaf.jpg" \
  | jq .
```

### Batch Processing

```python
import os
import requests
import pandas as pd

# Directory with images
image_dir = "images/"
results = []

# Process all images
for filename in os.listdir(image_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        filepath = os.path.join(image_dir, filename)
        
        with open(filepath, "rb") as f:
            files = {"file": f}
            response = requests.post("http://localhost:5000/api/predict", files=files)
            data = response.json()
            
            results.append({
                'filename': filename,
                'disease': data['prediction']['predicted_class'],
                'confidence': data['prediction']['confidence']
            })

# Save to CSV
df = pd.DataFrame(results)
df.to_csv('batch_results.csv', index=False)
print(f"Processed {len(results)} images")
```

---

## Best Practices

### Image Capture

1. **Timing**
   - Take photos during daylight (10 AM - 4 PM)
   - Avoid direct harsh sunlight
   - Cloudy days provide even lighting

2. **Distance**
   - 15-30 cm from leaf
   - Fill frame with affected area
   - Include some healthy tissue for comparison

3. **Angle**
   - Perpendicular to leaf surface
   - Avoid shadows
   - Show top side of leaf (usually)

4. **Focus**
   - Tap to focus on smartphone
   - Ensure disease symptoms are sharp
   - Use macro mode if available

### Disease Management

1. **Early Detection**
   - Check plants weekly
   - Look for early symptoms
   - Upload images at first sign of trouble

2. **Quarantine**
   - Isolate infected plants
   - Prevent spread to healthy plants
   - Dispose of severely infected material

3. **Treatment**
   - Follow recommendations exactly
   - Don't skip treatments
   - Monitor progress after 7-10 days
   - Re-analyze if condition worsens

4. **Prevention**
   - Maintain proper spacing
   - Ensure good air circulation
   - Practice crop rotation
   - Use disease-resistant varieties

### Record Keeping

1. **Document Progress**
   - Take photos before treatment
   - Photo every 3-5 days during treatment
   - Track which treatments work

2. **Track Patterns**
   - Note when diseases appear (season, weather)
   - Identify problem areas in field
   - Share data with extension services

---

## Troubleshooting

### Issue: "Model not found" error

**Solution:**
1. Ensure you've run the Jupyter notebook to train the model
2. Check that one of these files exists:
   - `best_chilli_disease_model.h5`
   - `chilli_disease_detection_model_final.h5`
   - `chilli_disease_detection_model_final.keras`
3. Place model file in the same directory as `app.py`

### Issue: Low confidence predictions

**Possible Causes:**
- Image quality is poor
- Disease symptoms not visible
- Unusual disease presentation
- Multiple diseases present

**Solutions:**
- Retake photo with better lighting
- Get closer to affected area
- Try different leaf showing clearer symptoms
- Consult agricultural expert if persistent

### Issue: Wrong disease identified

**Possible Causes:**
- Similar symptoms across diseases
- Mixed infections
- Non-disease stress (nutrient deficiency, drought)

**Solutions:**
- Check "All Probabilities" section for alternatives
- Consider top 3 predictions
- Consult symptoms list for each disease
- Get professional diagnosis for valuable crops

### Issue: Application runs slowly

**Solutions:**
1. Close other applications
2. Ensure sufficient RAM available
3. Use smaller images (<5MB)
4. Check internet connection
5. Restart application

### Issue: Upload fails

**Checks:**
- File size under 16MB
- File format is JPG, JPEG, or PNG
- File is not corrupted
- Browser permissions allow file uploads

---

## FAQ

### General Questions

**Q: Is this free to use?**  
A: Yes, the current version is completely free and open-source.

**Q: Do I need internet to use this?**  
A: After initial setup, the application runs locally without internet.

**Q: Is my data stored or shared?**  
A: No. Images are processed locally and not stored or transmitted anywhere.

**Q: How accurate is the detection?**  
A: The model achieves 95%+ accuracy on test data. Real-world performance depends on image quality.

**Q: Can I use this for other crops?**  
A: Currently optimized for chilli plants only. Contact us for custom models.

### Technical Questions

**Q: What model architecture is used?**  
A: Custom Convolutional Neural Network (CNN) with 4 conv blocks, BatchNorm, and Dropout layers.

**Q: What framework powers this?**  
A: TensorFlow 2.15 with Keras for the model, Flask for the web interface.

**Q: Can I retrain the model?**  
A: Yes! Use the included Jupyter notebook with your own dataset.

**Q: Is there an offline mobile app?**  
A: Not yet, but it's on our roadmap. Current web app is mobile-responsive.

**Q: Can I integrate this into my farm management software?**  
A: Yes, use our REST API. See API documentation.

### Agricultural Questions

**Q: Should I rely solely on AI diagnosis?**  
A: AI is a powerful tool but not a replacement for professional agronomists. Use it as a first-line screening tool.

**Q: What if the model identifies my plant as healthy but I see symptoms?**  
A: Some diseases may be early-stage or not in our training dataset. Consult a local agricultural extension service.

**Q: Are the organic treatments as effective as chemical ones?**  
A: Organic treatments work well for prevention and mild cases. Severe infections may require stronger interventions.

**Q: How often should I check my plants?**  
A: Weekly inspections during growing season. More frequently during periods of high disease pressure (humid, rainy weather).

---

## Support & Resources

### Getting Help
- **GitHub Issues:** [Report bugs or request features](https://github.com/yourusername/chillidoc-ai/issues)
- **Email:** support@chillidocai.com
- **Documentation:** [Full docs](https://docs.chillidocai.com)

### Additional Resources
- [Plant Disease Management Guide](https://example.com/guide)
- [Organic Farming Practices](https://example.com/organic)
- [Local Agricultural Extension Services](https://extension.org/)

### Community
- [Discord Server](https://discord.gg/chillidocai)
- [Forum](https://forum.chillidocai.com)
- [Facebook Group](https://facebook.com/groups/chillidocai)

---

## Appendix

### Disease Quick Reference

| Disease | Key Symptoms | Severity | First Action |
|---------|--------------|----------|--------------|
| Anthracnose | Dark spots on fruits | High | Remove infected fruits |
| Leaf Curl Virus | Curled, distorted leaves | Very High | Remove entire plant |
| Whitefly | Small white insects on leaves | Medium | Yellow sticky traps |
| Yellowing | Yellow leaves | High | Fertilize with nitrogen |
| Healthy | Green, vigorous growth | None | Continue current care |

### Recommended Products

#### Organic
- Neem Oil: 3-5 ml per liter water
- Baking Soda: 1 tbsp per liter for fungal diseases
- Garlic Spray: Homemade pest deterrent

#### Conventional
- Copper-based fungicides: For anthracnose
- Systemic insecticides: For whitefly and viruses
- Balanced fertilizer (19-19-19): For yellowing

**Always follow local regulations and product labels.**

---

**Last Updated:** December 2025  
**Version:** 1.0.0

---

*For the latest version of this guide, visit: https://docs.chillidocai.com*
