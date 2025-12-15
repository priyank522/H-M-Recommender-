# H-M-Recommender-
# 🛍️ H&M Personalized Fashion Recommender System

A production-style personalized recommender system built using the  
**H&M Personalized Fashion Recommendations** dataset.

This project combines **Collaborative Filtering (ALS)**, **Co-purchase modeling**, and  
**LightGBM learning-to-rank**, served through a **Streamlit web application** inspired by the H&M website UI.

---

## 🚀 Features

- Personalized recommendations using ALS Collaborative Filtering
- **“Users also bought”** recommendations via co-purchase modeling
- Learning-to-rank using **LightGBM**
- Product search (name / color / category)
- Product images & metadata
- Session-based cart system
- H&M-style UI using Streamlit
- Optimized for fast inference (no retraining required)

-  -## 🧠 System Architecture  ##
  
-  Kaggle Dataset (Local)
│
▼
Candidate Generation (ALS + Co-purchase)
│
▼
Feature Engineering
│
▼
LightGBM Ranker
│
▼
Streamlit Web Application


---

## 📂 Repository Structure

HM-Recommender/
├── app.py
├── README.md
├── requirements.txt
├── models/
│ ├── als_model.pkl
│ ├── lgbm_model.joblib
│ ├── user_encoder.joblib
│ ├── item_encoder.joblib
│ ├── co_purchase.joblib
│ ├── candidates.joblib
│ ├── user_summary.parquet
│ └── hm_logo.png
└── data/ (not uploaded)

--## 🧠 System Architecture

---

## 📦 Dataset Information (IMPORTANT)

 **The dataset is very large (multiple GBs)** and is therefore **NOT uploaded to this repository**

### Dataset Source
- Kaggle:  
  https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
  Dataset Files

**transactions_train.csv**
~31M purchase records with customer_id, article_id, price, and date

**customers.csv**
1,362,281 customers with basic demographic attributes

**articles.csv**
105,542 products with rich metadata (category, color, product type)

**images/**
Product images stored as article_id.jpg in subfolders

Usage in This Project

Transactions → collaborative filtering & co-purchase models

Articles → product search, similarity, and UI display

Images → product cards in the Streamlit app

**⚠️ Note**: The dataset is very large (multiple GBs) and is not included in this repository.
Models were trained locally, and only the trained artifacts are uploaded.

### Used for:
- Model training (offline, local)
- Feature engineering

📌 **Only trained models are uploaded**, which are sufficient to run the Streamlit app.

---

## 🖥️ Running the App Locally
-- 



