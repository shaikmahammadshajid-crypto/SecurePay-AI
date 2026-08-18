# SecurePay AI - Final Project Presentation

## Slide 1: Title

**SecurePay AI: AI-Powered Credit Card Fraud Detection System**

Presented by: Shaik Mahammad Shajid  
Department: B.Tech Computer Science and Engineering - Data Science  
Project Type: Final Year Machine Learning Web Application

## Slide 2: Main Task of the Project

The main task of SecurePay AI is to detect potentially fraudulent credit card transactions using machine learning.

The system accepts transaction features, preprocesses them using a trained scaler, predicts whether the transaction is genuine or fraudulent, calculates fraud probability, assigns a risk level, recommends action, and stores the result for future audit.

## Slide 3: Problem Statement

Credit card fraud causes financial loss to banks, merchants, and customers.

Fraud cases are rare compared to genuine transactions, which makes fraud detection difficult. A simple accuracy score can be misleading because a model can appear accurate by predicting most transactions as genuine. The project focuses on practical fraud triage using probability, risk level, recommendations, and audit history.

## Slide 4: Proposed Solution

SecurePay AI provides an end-to-end fraud review workflow:

- User authentication
- Single transaction prediction
- Batch CSV fraud screening
- Fraud probability and risk classification
- AI-based recommendation for next action
- Prediction history and profile summary
- Admin monitoring dashboard
- PDF audit report generation
- AI Assistant command center
- Health check endpoint for deployment readiness

## Slide 5: Technology Stack

- Frontend: HTML templates and CSS
- Backend: Flask
- Production Server: Gunicorn
- Hosting: Render
- Machine Learning: scikit-learn Random Forest
- Data Processing: Pandas and NumPy
- Model Storage: Joblib
- Database: SQLite
- Security: bcrypt password hashing
- Reports: ReportLab PDF generation
- Testing: Pytest

## Slide 6: Machine Learning Workflow

1. Transaction data is entered manually or uploaded as CSV.
2. Required features are validated: Time, V1 to V28, and Amount.
3. Values are converted to numeric format.
4. Data is scaled using the trained scaler.
5. Random Forest predicts class 0 or class 1.
6. Fraud probability is converted into a percentage.
7. The app generates risk level and recommendation.
8. Result is stored in SQLite prediction history.

## Slide 7: Model Information

Algorithm: Random Forest Classifier  
Dataset Type: European credit card fraud dataset  
Features: 30 transaction features  
Output: Binary classification  

Class meaning:

- 0 means Genuine Transaction
- 1 means Fraud Transaction

V1 to V28 are anonymized PCA-transformed features. Time and Amount are visible transaction attributes.

## Slide 8: User Roles

Normal User:

- Register and login
- Predict single transactions
- Upload batch CSV files
- View profile and history
- Generate audit report
- Use AI Assistant

Admin:

- View users
- View prediction logs
- Monitor fraud counts
- Monitor batch jobs

## Slide 9: Main Features

Single Prediction:

- User enters transaction features.
- The model returns fraud/genuine prediction.
- App displays probability, risk level, and action recommendation.

Batch Prediction:

- User uploads CSV.
- App scores all rows.
- Results can be downloaded as CSV.

History:

- Every single prediction is stored for audit.

AI Assistant:

- Can open pages, check health, summarize activity, run model test, and generate audit report.

## Slide 10: AI Assistant

The AI Assistant is a command center inside the app.

Example commands:

- check app health
- summarize my activity
- generate my audit report
- open batch prediction
- test model

It performs safe app actions directly. Sensitive decisions, such as final payment approval or blocking, remain user-reviewed.

## Slide 11: Security Features

- Passwords are stored as bcrypt hashes.
- Usernames are normalized to lowercase.
- Email validation is applied during registration.
- Protected pages require login.
- Admin pages require admin role.
- Prediction history is user-specific.
- Render environment variables can protect admin password and secret key.

## Slide 12: Reliability Features

- Central feature validation for single and batch predictions.
- Checks for missing columns, invalid numbers, NaN, infinite values, negative Time, and negative Amount.
- Model and scaler artifact health checks.
- SQLite database health check.
- Pytest suite validates auth, prediction, model loading, assistant intents, Flask routes, runtime config, and health helpers.

## Slide 13: Render Deployment

The project is deployed as a Render Python web service.

Production command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

Health endpoint:

```text
/health
```

The app no longer runs on Streamlit. It is a Flask web application served by Gunicorn on Render.

## Slide 14: How to Demonstrate

1. Open the live Render URL.
2. Open Reviewer Guide.
3. Register a new account.
4. Open Predict.
5. Click Baseline Review Transaction.
6. Submit prediction.
7. Explain prediction, probability, risk level, and recommendation.
8. Open History.
9. Open AI Assistant.
10. Run health check, summary, and audit report commands.

## Slide 15: Testing Summary

The latest test suite contains checks for:

- Authentication
- Password hashing
- Email validation
- Prediction feature validation
- Batch CSV validation
- Model artifact loading
- AI assistant command detection
- Flask login page
- Health endpoint
- Runtime config without Streamlit

Command:

```bash
python -m pytest -q
```

## Slide 16: Limitations

- The model depends on the quality and distribution of the training dataset.
- Real banking deployment would require live transaction streams, device data, merchant data, IP/location signals, and stronger monitoring.
- SQLite is suitable for project demonstration but production banking systems should use managed databases.
- Fraud models should be continuously retrained and monitored.

## Slide 17: Future Enhancements

- Add real-time banking API integration.
- Add advanced explainability such as SHAP/LIME in the Flask interface.
- Add role-based case management.
- Add alert notifications for high-risk predictions.
- Add persistent cloud database.
- Add model performance dashboard from real evaluation reports.
- Add API endpoints for external transaction systems.

## Slide 18: Conclusion

SecurePay AI is a complete, meaningful final-year project because it solves a real-world financial cybersecurity problem using machine learning and deploys it as a usable web application.

It is not only a prediction model. It includes authentication, prediction workflow, batch screening, audit history, admin monitoring, report generation, AI assistance, testing, and Render deployment.

## Short Viva Answers

**What is the main aim of this project?**  
To detect credit card fraud using machine learning and support fraud review through probability, risk levels, recommendations, history, and reports.

**Why Random Forest?**  
Random Forest handles nonlinear patterns, works well for tabular data, reduces overfitting compared with a single decision tree, and gives reliable classification performance for this type of dataset.

**Why is accuracy alone not enough?**  
Fraud data is highly imbalanced. A model can show high accuracy by predicting most transactions as genuine, so recall, precision, F1 score, ROC-AUC, and confusion matrix are more meaningful.

**What does Class mean?**  
Class 0 means genuine transaction. Class 1 means fraudulent transaction.

**What are V1 to V28?**  
They are anonymized PCA-transformed transaction features from the original fraud dataset.

**What makes this project AI-based?**  
It uses a trained machine-learning classifier to make fraud predictions and combines the prediction with assistant-driven recommendations and workflow automation.

**How is the project deployed?**  
It is deployed on Render as a Flask web app served by Gunicorn.

**Is the model 100% accurate?**  
No responsible fraud model should claim guaranteed 100% accuracy. The project uses measurable testing and evaluation methods to analyze performance.

## Final Demo Script

"This is SecurePay AI, an AI-powered credit card fraud detection system. The main task is to classify card transactions as genuine or fraudulent. A user logs in, enters transaction features or uploads a CSV file, and the trained Random Forest model predicts fraud probability. The app then converts that probability into a risk level and recommendation. Every prediction is saved in history for audit. The AI Assistant helps users navigate the app, check system health, summarize activity, test the model, and generate reports. The project is deployed on Render using Flask and Gunicorn, and it includes automated tests for reliability."
