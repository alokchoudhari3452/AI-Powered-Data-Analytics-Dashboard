from flask import Flask, request, jsonify, send_file
import mysql.connector
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
import os
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.cluster import KMeans


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )
CORS(app)
@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            "success": True,
            "message": "MySQL connected successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        # Hash password before storing it
        from werkzeug.security import generate_password_hash

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()

            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 409

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Registration successful"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# GET LATEST DATASET
# ============================================================

def get_latest_file():

    files = []

    for filename in os.listdir(UPLOAD_FOLDER):

        if filename.startswith("cleaned_"):
            continue

        if not filename.lower().endswith(
            (".csv", ".xlsx", ".xls")
        ):
            continue

        full_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if not os.path.isfile(full_path):
            continue

        if os.path.getsize(full_path) == 0:
            continue

        files.append(full_path)

    if not files:

        raise FileNotFoundError(
            "No valid CSV or Excel dataset found in uploads folder."
        )

    files.sort(
        key=os.path.getmtime,
        reverse=True
    )

    return files[0]


# ============================================================
# READ DATASET
# ============================================================

def read_dataset(filepath=None):

    filepath = get_latest_file()

    extension = os.path.splitext(
        filepath
    )[1].lower()

    if extension == ".csv":

        df = pd.read_csv(filepath)

    elif extension in [".xlsx", ".xls"]:

        df = pd.read_excel(filepath)

    else:

        raise ValueError(
            "Unsupported file format."
        )

    if df.empty:

        raise ValueError(
            "Dataset is empty."
        )

    return df


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "message":
        "AI-Powered Data Analytics Dashboard API is running.",
        "status":
        "success"
    })


# ============================================================
# UPLOAD
# ============================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    try:

        if "file" not in request.files:

            return jsonify({
                "error":
                "No file uploaded."
            }), 400

        file = request.files["file"]

        if file.filename == "":

            return jsonify({
                "error":
                "No file selected."
            }), 400

        allowed_extensions = [
            ".csv",
            ".xlsx",
            ".xls"
        ]

        extension = os.path.splitext(
            file.filename
        )[1].lower()

        if extension not in allowed_extensions:

            return jsonify({
                "error":
                "Only CSV and Excel files are allowed."
            }), 400

        filepath = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(filepath)

        # Get logged-in user ID
        user_id = request.form.get("user_id")

        if user_id:

            df = read_dataset(filepath)

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO analysis_history
                (user_id, file_name, rows_count, columns_count)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    int(user_id),
                    file.filename,
                    len(df),
                    len(df.columns)
                )
            )

            conn.commit()

            cursor.close()
            conn.close()

        return jsonify({

            "message":
            "File uploaded successfully.",

            "filename":
            file.filename

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# ANALYZE
# ============================================================

@app.route("/analyze")
def analyze():

    try:

        df = read_dataset()

        missing_values = int(
            df.isnull().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        return jsonify({

            "filename":
            os.path.basename(
                get_latest_file()
            ),

            "rows":
            int(df.shape[0]),

            "columns":
            int(df.shape[1]),

            "column_names":
            list(df.columns),

            "missing_values":
            missing_values,

            "duplicate_rows":
            duplicate_rows,

            "data_types":
            {
                col: str(dtype)
                for col, dtype in df.dtypes.items()
            }

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# DATA CLEANING
# ============================================================

@app.route("/clean")
def clean():

    try:

        df = read_dataset()

        original_rows = len(df)

        duplicate_count = int(
            df.duplicated().sum()
        )

        df = df.drop_duplicates()

        missing_before = int(
            df.isnull().sum().sum()
        )

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns

        categorical_columns = df.select_dtypes(
            exclude=np.number
        ).columns

        for column in numeric_columns:

            if df[column].isnull().any():

                df[column] = df[column].fillna(
                    df[column].median()
                )

        for column in categorical_columns:

            if df[column].isnull().any():

                mode = df[column].mode()

                if not mode.empty:

                    df[column] = df[column].fillna(
                        mode[0]
                    )

        missing_after = int(
            df.isnull().sum().sum()
        )

        filename = os.path.basename(
            get_latest_file()
        )

        cleaned_filename = (
            "cleaned_" + filename
        )

        cleaned_path = os.path.join(
            UPLOAD_FOLDER,
            cleaned_filename
        )

        df.to_csv(
            cleaned_path,
            index=False
        )

        return jsonify({

            "message":
            "Dataset cleaned successfully.",

            "original_rows":
            int(original_rows),

            "final_rows":
            int(len(df)),

            "duplicates_removed":
            int(duplicate_count),

            "missing_values_before":
            int(missing_before),

            "missing_values_after":
            int(missing_after),

            "cleaned_file":
            cleaned_filename

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# OUTLIER DETECTION
# ============================================================

@app.route("/outliers")
def outliers():

    try:

        df = read_dataset()

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns

        if len(numeric_columns) == 0:

            return jsonify({
                "error":
                "No numeric columns available."
            }), 400

        result = {}

        for column in numeric_columns:

            Q1 = df[column].quantile(0.25)

            Q3 = df[column].quantile(0.75)

            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR

            upper_bound = Q3 + 1.5 * IQR

            outlier_rows = df[
                (df[column] < lower_bound)
                |
                (df[column] > upper_bound)
            ]

            result[column] = {

                "outlier_count":
                int(len(outlier_rows)),

                "lower_bound":
                float(lower_bound),

                "upper_bound":
                float(upper_bound)

            }

        return jsonify({

            "outliers":
            result

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# STATISTICS
# ============================================================

@app.route("/statistics")
def statistics():

    try:

        df = read_dataset()

        numeric_df = df.select_dtypes(
            include=np.number
        )

        if numeric_df.empty:

            return jsonify({
                "error":
                "No numeric columns available."
            }), 400

        description = numeric_df.describe()

        result = {}

        for column in description.columns:

            result[column] = {

                "count":
                float(description.loc["count", column]),

                "mean":
                float(description.loc["mean", column]),

                "std":
                float(description.loc["std", column]),

                "min":
                float(description.loc["min", column]),

                "25%":
                float(description.loc["25%", column]),

                "50%":
                float(description.loc["50%", column]),

                "75%":
                float(description.loc["75%", column]),

                "max":
                float(description.loc["max", column])

            }

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CHART 1
# TOTAL SPENDING BY CUSTOMER
# ============================================================

@app.route("/chart")
def chart():

    try:

        df = read_dataset()

        required_columns = [
            "Customer_ID",
            "Total_Spending"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        data = []

        for _, row in df.iterrows():

            data.append({

                "Customer_ID":
                float(row["Customer_ID"]),

                "Total_Spending":
                float(row["Total_Spending"])

            })

        return jsonify({

            "data":
            data

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CHART 2
# MONTHLY INCOME VS TOTAL SPENDING
# ============================================================

@app.route("/income-spending")
def income_spending():

    try:

        df = read_dataset()

        required_columns = [
            "Monthly_Income",
            "Total_Spending"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        data = df[
            required_columns
        ].dropna()

        result = []

        for _, row in data.iterrows():

            result.append({

                "Monthly_Income":
                float(row["Monthly_Income"]),

                "Total_Spending":
                float(row["Total_Spending"])

            })

        return jsonify({

            "data":
            result

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CHART 3
# ORDERS BY CITY
# ============================================================

@app.route("/orders-city")
def orders_city():

    try:

        df = read_dataset()

        required_columns = [
            "City",
            "Orders"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        grouped = (
            df.groupby("City")["Orders"]
            .sum()
            .reset_index()
        )

        result = []

        for _, row in grouped.iterrows():

            result.append({

                "City":
                str(row["City"]),

                "Orders":
                float(row["Orders"])

            })

        return jsonify({

            "data":
            result

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CHART 4
# SATISFACTION BY CITY
# ============================================================

@app.route("/satisfaction-city")
def satisfaction_city():

    try:

        df = read_dataset()

        required_columns = [
            "City",
            "Satisfaction"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        grouped = (
            df.groupby("City")["Satisfaction"]
            .mean()
            .reset_index()
        )

        result = []

        for _, row in grouped.iterrows():

            result.append({

                "City":
                str(row["City"]),

                "Satisfaction":
                float(row["Satisfaction"])

            })

        return jsonify({

            "data":
            result

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CORRELATION
# ============================================================

@app.route("/correlation")
def correlation():

    try:

        df = read_dataset()

        numeric_df = df.select_dtypes(
            include=np.number
        )

        if numeric_df.empty:

            return jsonify({
                "error":
                "No numeric columns available."
            }), 400

        corr = numeric_df.corr()

        result = {}

        for column in corr.columns:

            result[column] = {}

            for other_column in corr.columns:

                value = corr.loc[
                    column,
                    other_column
                ]

                if pd.isna(value):

                    result[column][
                        other_column
                    ] = None

                else:

                    result[column][
                        other_column
                    ] = round(
                        float(value),
                        4
                    )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# MACHINE LEARNING COLUMNS
# ============================================================

@app.route("/ml/columns")
def ml_columns():

    try:

        df = read_dataset()

        return jsonify({

            "columns":
            list(df.columns),

            "numeric_columns":
            list(
                df.select_dtypes(
                    include=np.number
                ).columns
            ),

            "categorical_columns":
            list(
                df.select_dtypes(
                    exclude=np.number
                ).columns
            )

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CLASSIFICATION
# ============================================================

@app.route("/ml/classification")
def classification():

    try:

        df = read_dataset()

        required_columns = [
            "Age",
            "Monthly_Income",
            "Orders",
            "Total_Spending",
            "Satisfaction"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        data = df[
            required_columns
        ].dropna()

        if len(data) < 6:

            return jsonify({
                "error":
                "Not enough data for classification."
            }), 400

        X = data[
            [
                "Age",
                "Monthly_Income",
                "Orders",
                "Total_Spending"
            ]
        ]

        y = np.where(
            data["Satisfaction"] >= 3,
            "Satisfied",
            "Not Satisfied"
        )

        unique_classes = np.unique(y)

        if len(unique_classes) < 2:

            return jsonify({

                "error":
                "Classification requires at least two classes.",

                "classes_found":
                unique_classes.tolist()

            }), 400

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        scaler = StandardScaler()

        X_train_scaled = scaler.fit_transform(
            X_train
        )

        X_test_scaled = scaler.transform(
            X_test
        )

        class_mapping = {
            "Not Satisfied": 0,
            "Satisfied": 1
        }

        y_train_numeric = np.array([
            class_mapping[value]
            for value in y_train
        ])

        y_test_numeric = np.array([
            class_mapping[value]
            for value in y_test
        ])

        model = LinearRegression()

        model.fit(
            X_train_scaled,
            y_train_numeric
        )

        predictions = model.predict(
            X_test_scaled
        )

        predicted_classes = np.where(
            predictions >= 0.5,
            1,
            0
        )

        accuracy = accuracy_score(
            y_test_numeric,
            predicted_classes
        )

        return jsonify({

            "model":
            "Linear Classification",

            "accuracy":
            round(
                float(accuracy * 100),
                2
            ),

            "training_rows":
            int(len(X_train)),

            "testing_rows":
            int(len(X_test)),

            "classes":
            unique_classes.tolist()

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# REGRESSION
# ============================================================

@app.route("/ml/regression")
def regression():

    try:

        df = read_dataset()

        required_columns = [
            "Age",
            "Monthly_Income",
            "Orders",
            "Total_Spending"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        data = df[
            required_columns
        ].dropna()

        if len(data) < 5:

            return jsonify({
                "error":
                "Not enough data for regression."
            }), 400

        X = data[
            [
                "Age",
                "Monthly_Income",
                "Orders"
            ]
        ]

        y = data[
            "Total_Spending"
        ]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        scaler = StandardScaler()

        X_train_scaled = scaler.fit_transform(
            X_train
        )

        X_test_scaled = scaler.transform(
            X_test
        )

        model = LinearRegression()

        model.fit(
            X_train_scaled,
            y_train
        )

        predictions = model.predict(
            X_test_scaled
        )

        r2 = model.score(
            X_test_scaled,
            y_test
        )

        mse = mean_squared_error(
            y_test,
            predictions
        )

        return jsonify({

            "model":
            "Linear Regression",

            "target":
            "Total_Spending",

            "r2_score":
            round(
                float(r2),
                2
            ),

            "mean_squared_error":
            round(
                float(mse),
                2
            ),

            "training_rows":
            int(len(X_train)),

            "testing_rows":
            int(len(X_test))

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# PREDICTION
# ============================================================

@app.route(
    "/ml/predict",
    methods=["POST"]
)
def predict():

    try:

        df = read_dataset()

        required_columns = [
            "Age",
            "Monthly_Income",
            "Orders",
            "Total_Spending"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        data = df[
            required_columns
        ].dropna()

        if len(data) < 5:

            return jsonify({
                "error":
                "Not enough data for prediction."
            }), 400

        input_data = request.get_json()

        if not input_data:

            return jsonify({
                "error":
                "No prediction data provided."
            }), 400

        age = float(
            input_data["Age"]
        )

        monthly_income = float(
            input_data["Monthly_Income"]
        )

        orders = float(
            input_data["Orders"]
        )

        X = data[
            [
                "Age",
                "Monthly_Income",
                "Orders"
            ]
        ]

        y = data[
            "Total_Spending"
        ]

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(
            X
        )

        model = LinearRegression()

        model.fit(
            X_scaled,
            y
        )

        new_customer = pd.DataFrame(
            [
                {
                    "Age": age,
                    "Monthly_Income": monthly_income,
                    "Orders": orders
                }
            ]
        )

        new_customer_scaled = scaler.transform(
            new_customer
        )

        prediction = model.predict(
            new_customer_scaled
        )

        predicted_value = float(
            prediction[0]
        )

        return jsonify({

            "prediction":
            round(
                predicted_value,
                2
            ),

            "predicted_total_spending":
            round(
                predicted_value,
                2
            )

        })

    except KeyError as e:

        return jsonify({
            "error":
            f"Missing input field: {str(e)}"
        }), 400

    except ValueError as e:

        return jsonify({
            "error":
            f"Invalid input: {str(e)}"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# CLUSTERING
# ============================================================

@app.route("/ml/clustering")
def clustering():

    try:

        df = read_dataset()

        required_columns = [
            "Age",
            "Monthly_Income",
            "Orders",
            "Total_Spending"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return jsonify({
                "error":
                f"Missing columns: {missing_columns}"
            }), 400

        data = df[
            required_columns
        ].dropna()

        if len(data) < 3:

            return jsonify({
                "error":
                "At least 3 valid rows are required for clustering."
            }), 400

        X = data[
            required_columns
        ]

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(
            X
        )

        number_of_clusters = min(
            3,
            len(data)
        )

        model = KMeans(
            n_clusters=number_of_clusters,
            random_state=42,
            n_init=10
        )

        clusters = model.fit_predict(
            X_scaled
        )

        result = []

        for index, cluster in enumerate(clusters):

            result.append({

                "row":
                int(index + 1),

                "cluster":
                int(cluster)

            })

        return jsonify({

            "model":
            "K-Means Clustering",

            "clusters":
            int(number_of_clusters),

            "data":
            result

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# RUN SERVER
# ============================================================
@app.route("/ai-insights", methods=["GET"])
def ai_insights():
    try:
        df = read_dataset()

        insights = []

        # Basic statistics
        if "Monthly_Income" in df.columns:
            avg_income = df["Monthly_Income"].mean()
            insights.append(
                f"Average monthly income is ₹{avg_income:,.2f}."
            )

        if "Total_Spending" in df.columns:
            avg_spending = df["Total_Spending"].mean()
            max_spending = df["Total_Spending"].max()

            insights.append(
                f"Average total spending is ₹{avg_spending:,.2f}."
            )

            insights.append(
                f"Highest recorded total spending is ₹{max_spending:,.2f}."
            )

        if "Orders" in df.columns:
            avg_orders = df["Orders"].mean()
            insights.append(
                f"Average number of orders per customer is {avg_orders:.2f}."
            )

        if "Satisfaction" in df.columns:
            avg_satisfaction = df["Satisfaction"].mean()
            insights.append(
                f"Average customer satisfaction score is {avg_satisfaction:.2f} out of 5."
            )

        # Correlation insight
        if "Monthly_Income" in df.columns and "Total_Spending" in df.columns:
            correlation = df["Monthly_Income"].corr(
                df["Total_Spending"]
            )

            if correlation >= 0.7:
                insights.append(
                    "Monthly income and total spending have a strong positive relationship."
                )
            elif correlation >= 0.3:
                insights.append(
                    "Monthly income and total spending have a moderate positive relationship."
                )
            elif correlation <= -0.3:
                insights.append(
                    "Monthly income and total spending have a negative relationship."
                )
            else:
                insights.append(
                    "Monthly income and total spending have a weak relationship."
                )

        # City insight
        if "City" in df.columns and "Total_Spending" in df.columns:
            city_spending = df.groupby("City")["Total_Spending"].mean()
            highest_city = city_spending.idxmax()

            insights.append(
                f"{highest_city} has the highest average total spending among the available cities."
            )

        return jsonify({
            "success": True,
            "insights": insights
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
@app.route("/generate-report", methods=["GET"])
def generate_report():
    try:
        df = read_dataset()

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        normal_style = styles["BodyText"]

        elements = []

        # Title
        elements.append(
            Paragraph(
                "AI-Powered Data Analytics Dashboard",
                title_style
            )
        )

        elements.append(Spacer(1, 20))

        elements.append(
            Paragraph(
                "Automated Data Analysis Report",
                heading_style
            )
        )

        elements.append(Spacer(1, 10))

        # Dataset Information
        elements.append(
            Paragraph(
                "1. Dataset Information",
                heading_style
            )
        )

        elements.append(
            Paragraph(
                f"Total Rows: {df.shape[0]}",
                normal_style
            )
        )

        elements.append(
            Paragraph(
                f"Total Columns: {df.shape[1]}",
                normal_style
            )
        )

        elements.append(Spacer(1, 10))

        # Dataset Columns
        elements.append(
            Paragraph(
                "Dataset Columns",
                heading_style
            )
        )

        column_data = [["Column Name"]]

        for column in df.columns:
            column_data.append([str(column)])

        column_table = Table(column_data)

        column_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ])
        )

        elements.append(column_table)

        elements.append(Spacer(1, 20))

        # Statistical Summary
        elements.append(
            Paragraph(
                "2. Statistical Summary",
                heading_style
            )
        )

        numeric_df = df.select_dtypes(include="number")

        if not numeric_df.empty:

            stats = numeric_df.describe().round(2)

            stats_data = [
                ["Metric"] + [str(col) for col in stats.columns]
            ]

            for index in stats.index:

                row = [str(index)]

                for column in stats.columns:
                    row.append(str(stats.loc[index, column]))

                stats_data.append(row)

            stats_table = Table(
                stats_data,
                repeatRows=1
            )

            stats_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                ])
            )

            elements.append(stats_table)

        elements.append(Spacer(1, 20))

        # AI Insights
        elements.append(
            Paragraph(
                "3. AI-Generated Insights",
                heading_style
            )
        )

        insights = []

        if "Monthly_Income" in df.columns:
            avg_income = df["Monthly_Income"].mean()

            insights.append(
                f"Average monthly income is Rs. {avg_income:,.2f}."
            )

        if "Total_Spending" in df.columns:
            avg_spending = df["Total_Spending"].mean()
            max_spending = df["Total_Spending"].max()

            insights.append(
                f"Average total spending is Rs. {avg_spending:,.2f}."
            )

            insights.append(
                f"Highest recorded total spending is Rs. {max_spending:,.2f}."
            )

        if "Orders" in df.columns:
            avg_orders = df["Orders"].mean()

            insights.append(
                f"Average number of orders per customer is {avg_orders:.2f}."
            )

        if "Satisfaction" in df.columns:
            avg_satisfaction = df["Satisfaction"].mean()

            insights.append(
                f"Average customer satisfaction score is "
                f"{avg_satisfaction:.2f} out of 5."
            )

        if (
            "Monthly_Income" in df.columns
            and "Total_Spending" in df.columns
        ):
            correlation = df["Monthly_Income"].corr(
                df["Total_Spending"]
            )

            if correlation >= 0.7:
                insights.append(
                    "Monthly income and total spending have "
                    "a strong positive relationship."
                )

            elif correlation >= 0.3:
                insights.append(
                    "Monthly income and total spending have "
                    "a moderate positive relationship."
                )

            elif correlation <= -0.3:
                insights.append(
                    "Monthly income and total spending have "
                    "a negative relationship."
                )

            else:
                insights.append(
                    "Monthly income and total spending have "
                    "a weak relationship."
                )

        if (
            "City" in df.columns
            and "Total_Spending" in df.columns
        ):
            city_spending = df.groupby("City")["Total_Spending"].mean()

            if not city_spending.empty:
                highest_city = city_spending.idxmax()

                insights.append(
                    f"{highest_city} has the highest average "
                    "total spending among the available cities."
                )

        for insight in insights:

            elements.append(
                Paragraph(
                    "• " + insight,
                    normal_style
                )
            )

            elements.append(Spacer(1, 5))

        elements.append(Spacer(1, 20))

        elements.append(
            Paragraph(
                "Generated automatically by AI-Powered Data Analytics Dashboard.",
                normal_style
            )
        )

        # Build PDF
        doc.build(elements)

        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="AI_Data_Analytics_Report.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400

        # Password verification
        from werkzeug.security import check_password_hash

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        # Check hashed password
        if not check_password_hash(
            user["password"],
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
@app.route("/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, file_name, rows_count, columns_count, created_at
            FROM analysis_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        history = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "history": history
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )