import { useState } from "react";
import axios from "axios";
import "./App.css";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
} from "recharts";

const API_URL = "http://127.0.0.1:5000";

function App() {
  // ============================================================
  // AUTHENTICATION
  // ============================================================

  const [registerData, setRegisterData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [registerMessage, setRegisterMessage] = useState("");

  const [loginData, setLoginData] = useState({
    email: "",
    password: "",
  });

  const [loginMessage, setLoginMessage] = useState("");

  const [loggedInUser, setLoggedInUser] = useState(null);
  
  const [history, setHistory] = useState([]);
  // ============================================================
  // FILE
  // ============================================================

  const [file, setFile] = useState(null);

  // ============================================================
  // ANALYSIS
  // ============================================================

  const [analysis, setAnalysis] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [correlation, setCorrelation] = useState(null);
  const [aiInsights, setAiInsights] = useState([]);

  // ============================================================
  // CHART DATA
  // ============================================================

  const [chartData, setChartData] = useState([]);
  const [incomeSpendingData, setIncomeSpendingData] = useState([]);
  const [ordersCityData, setOrdersCityData] = useState([]);
  const [satisfactionCityData, setSatisfactionCityData] = useState([]);

  // ============================================================
  // CLEANING / OUTLIERS
  // ============================================================

  const [cleaningResult, setCleaningResult] = useState(null);
  const [outlierResult, setOutlierResult] = useState(null);

  // ============================================================
  // MACHINE LEARNING
  // ============================================================

  const [mlColumns, setMlColumns] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null);
  const [regressionResult, setRegressionResult] = useState(null);
  const [clusteringResult, setClusteringResult] = useState(null);

  // ============================================================
  // PREDICTION
  // ============================================================

  const [predictionData, setPredictionData] = useState({
    Age: "",
    Monthly_Income: "",
    Orders: "",
  });

  const [predictionResult, setPredictionResult] = useState(null);

  // ============================================================
  // LOADING
  // ============================================================

  const [loading, setLoading] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [outlierLoading, setOutlierLoading] = useState(false);
  const [statisticsLoading, setStatisticsLoading] = useState(false);
  const [classificationLoading, setClassificationLoading] =
    useState(false);
  const [regressionLoading, setRegressionLoading] = useState(false);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [clusteringLoading, setClusteringLoading] = useState(false);

  // ============================================================
  // REGISTER
  // ============================================================

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        `${API_URL}/register`,
        registerData
      );

      setRegisterMessage(response.data.message);

      setRegisterData({
        name: "",
        email: "",
        password: "",
      });
    } catch (error) {
      setRegisterMessage(
        error.response?.data?.message ||
          "Registration failed"
      );
    }
  };

  // ============================================================
  // LOGIN
  // ============================================================

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        `${API_URL}/login`,
        loginData
      );

      if (response.data.success) {
        setLoggedInUser(response.data.user);
        setLoginMessage(response.data.message);
        await axios
  .get(`${API_URL}/history/${response.data.user.id}`)
  .then((historyResponse) => {
    setHistory(
      historyResponse.data.history || []
    );
  });
        setLoginData({
          email: "",
          password: "",
        });
      } else {
        setLoginMessage(
          response.data.message || "Login failed"
        );
      }
    } catch (error) {
      setLoginMessage(
        error.response?.data?.message ||
          "Login failed"
      );
    }
  };

  // ============================================================
  // LOGOUT
  // ============================================================

  const handleLogout = () => {
    setLoggedInUser(null);
    setLoginMessage("");
  };
  const loadHistory = async () => {
  if (!loggedInUser) {
    return;
  }

  try {
    const response = await axios.get(
      `${API_URL}/history/${loggedInUser.id}`
    );

    setHistory(
      response.data.history || []
    );
  } catch (error) {
    console.error(
      "History Error:",
      error
    );
  }
};

  // ============================================================
  // FILE CHANGE
  // ============================================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setFile(selectedFile);

    setAnalysis(null);
    setStatistics(null);
    setCorrelation(null);

    setChartData([]);
    setIncomeSpendingData([]);
    setOrdersCityData([]);
    setSatisfactionCityData([]);

    setCleaningResult(null);
    setOutlierResult(null);

    setMlColumns(null);
    setClassificationResult(null);
    setRegressionResult(null);
    setPredictionResult(null);
    setClusteringResult(null);

    setPredictionData({
      Age: "",
      Monthly_Income: "",
      Orders: "",
    });
  };

  // ============================================================
  // STATISTICS
  // ============================================================

  const loadStatistics = async () => {
    try {
      setStatisticsLoading(true);

      const response = await axios.get(
        `${API_URL}/statistics`
      );

      setStatistics(response.data);
    } catch (error) {
      console.error(
        "Statistics Error:",
        error
      );
    } finally {
      setStatisticsLoading(false);
    }
  };

  // ============================================================
  // AI INSIGHTS
  // ============================================================

  const loadAIInsights = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/ai-insights`
      );

      setAiInsights(
        response.data.insights || []
      );
    } catch (error) {
      console.error(
        "AI Insights Error:",
        error
      );
    }
  };

  // ============================================================
  // CORRELATION
  // ============================================================

  const loadCorrelation = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/correlation`
      );

      setCorrelation(response.data);
    } catch (error) {
      console.error(
        "Correlation Error:",
        error
      );
    }
  };

  // ============================================================
  // ML COLUMNS
  // ============================================================

  const loadMLColumns = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/ml/columns`
      );

      setMlColumns(response.data);
    } catch (error) {
      console.error(
        "ML Columns Error:",
        error
      );
    }
  };

  // ============================================================
  // LOAD CHARTS
  // ============================================================

  const loadCharts = async () => {
    try {
      const chartResponse = await axios.get(
        `${API_URL}/chart`
      );

      if (
        chartResponse.data &&
        Array.isArray(chartResponse.data.data)
      ) {
        setChartData(chartResponse.data.data);
      } else {
        setChartData([]);
      }

      const incomeResponse = await axios.get(
        `${API_URL}/income-spending`
      );

      if (
        incomeResponse.data &&
        Array.isArray(incomeResponse.data.data)
      ) {
        setIncomeSpendingData(
          incomeResponse.data.data
        );
      } else {
        setIncomeSpendingData([]);
      }

      const ordersResponse = await axios.get(
        `${API_URL}/orders-city`
      );

      if (
        ordersResponse.data &&
        Array.isArray(ordersResponse.data.data)
      ) {
        setOrdersCityData(
          ordersResponse.data.data
        );
      } else {
        setOrdersCityData([]);
      }

      const satisfactionResponse = await axios.get(
        `${API_URL}/satisfaction-city`
      );

      if (
        satisfactionResponse.data &&
        Array.isArray(
          satisfactionResponse.data.data
        )
      ) {
        setSatisfactionCityData(
          satisfactionResponse.data.data
        );
      } else {
        setSatisfactionCityData([]);
      }
    } catch (error) {
      console.error(
        "Chart Error:",
        error
      );
    }
  };

  // ============================================================
  // UPLOAD + ANALYSIS
  // ============================================================

const handleUpload = async () => {
  if (!file) {
    alert(
      "Please select a CSV or Excel file."
    );
    return;
  }

  if (!loggedInUser) {
    alert(
      "Please login before uploading a dataset."
    );
    return;
  }

  try {
    setLoading(true);

    const formData = new FormData();

    formData.append("file", file);

    // Send logged-in user's ID to Flask
    formData.append(
      "user_id",
      loggedInUser.id
    );

    await axios.post(
      `${API_URL}/upload`,
      formData
    );

    const analysisResponse =
      await axios.get(
        `${API_URL}/analyze`
      );

    setAnalysis(
      analysisResponse.data
    );

    await loadStatistics();
    await loadCorrelation();
    await loadMLColumns();
    await loadCharts();
    await loadAIInsights();

    alert(
      "Dataset uploaded and analyzed successfully!"
    );
  } catch (error) {
    console.error(
      "Upload Error:",
      error
    );

    alert(
      error.response?.data?.error ||
        "Upload or analysis failed."
    );
  } finally {
    setLoading(false);
  }
};
  // ============================================================
  // DATA CLEANING
  // ============================================================

  const handleCleaning = async () => {
    try {
      setCleaning(true);
      setCleaningResult(null);

      const response = await axios.get(
        `${API_URL}/clean`
      );

      setCleaningResult(
        response.data
      );
    } catch (error) {
      console.error(
        "Cleaning Error:",
        error
      );

      setCleaningResult({
        error:
          error.response?.data?.error ||
          "Data cleaning failed.",
      });
    } finally {
      setCleaning(false);
    }
  };

  // ============================================================
  // OUTLIERS
  // ============================================================

  const handleOutliers = async () => {
    try {
      setOutlierLoading(true);
      setOutlierResult(null);

      const response = await axios.get(
        `${API_URL}/outliers`
      );

      setOutlierResult(
        response.data
      );
    } catch (error) {
      console.error(
        "Outlier Error:",
        error
      );

      setOutlierResult({
        error:
          error.response?.data?.error ||
          "Outlier detection failed.",
      });
    } finally {
      setOutlierLoading(false);
    }
  };

  // ============================================================
  // CLASSIFICATION
  // ============================================================

  const handleClassification = async () => {
    try {
      setClassificationLoading(true);
      setClassificationResult(null);

      const response = await axios.get(
        `${API_URL}/ml/classification`
      );

      setClassificationResult(
        response.data
      );
    } catch (error) {
      console.error(
        "Classification Error:",
        error
      );

      setClassificationResult({
        error:
          error.response?.data?.error ||
          "Classification failed.",
      });
    } finally {
      setClassificationLoading(false);
    }
  };

  // ============================================================
  // REGRESSION
  // ============================================================

  const handleRegression = async () => {
    try {
      setRegressionLoading(true);
      setRegressionResult(null);

      const response = await axios.get(
        `${API_URL}/ml/regression`
      );

      setRegressionResult(
        response.data
      );
    } catch (error) {
      console.error(
        "Regression Error:",
        error
      );

      setRegressionResult({
        error:
          error.response?.data?.error ||
          "Regression failed.",
      });
    } finally {
      setRegressionLoading(false);
    }
  };

  // ============================================================
  // PREDICTION
  // ============================================================

  const handlePrediction = async () => {
    if (
      predictionData.Age === "" ||
      predictionData.Monthly_Income === "" ||
      predictionData.Orders === ""
    ) {
      alert(
        "Please enter Age, Monthly Income and Orders."
      );

      return;
    }

    try {
      setPredictionLoading(true);
      setPredictionResult(null);

      const response = await axios.post(
        `${API_URL}/ml/predict`,
        {
          Age: Number(
            predictionData.Age
          ),
          Monthly_Income: Number(
            predictionData.Monthly_Income
          ),
          Orders: Number(
            predictionData.Orders
          ),
        }
      );

      setPredictionResult(
        response.data
      );
    } catch (error) {
      console.error(
        "Prediction Error:",
        error
      );

      setPredictionResult({
        error:
          error.response?.data?.error ||
          "Prediction failed.",
      });
    } finally {
      setPredictionLoading(false);
    }
  };

  // ============================================================
  // CLUSTERING
  // ============================================================

  const handleClustering = async () => {
    try {
      setClusteringLoading(true);
      setClusteringResult(null);

      const response = await axios.get(
        `${API_URL}/ml/clustering`
      );

      setClusteringResult(
        response.data
      );
    } catch (error) {
      console.error(
        "Clustering Error:",
        error
      );

      setClusteringResult({
        error:
          error.response?.data?.error ||
          "Clustering failed.",
      });
    } finally {
      setClusteringLoading(false);
    }
  };

  // ============================================================
  // MAIN UI
  // ============================================================

  return (
    <div className="app">

      {/* ======================================================
          HEADER
      ====================================================== */}
<header className="header">

  <div>
    <h1>
      🤖 AI-Powered Data Analytics Dashboard
    </h1>

    <p>
      Upload your dataset, analyze data,
      visualize results and perform machine learning.
    </p>
  </div>

  <nav className="dashboard-nav">
    <a href="#upload">Upload</a>
    <a href="#analysis">Analysis</a>
    <a href="#charts">Charts</a>
    <a href="#history">History</a>
  </nav>

</header>
      {/* ======================================================
          AUTHENTICATION
      ====================================================== */}

      <section className="data-section">

        <h2>🔐 User Authentication</h2>

        {loggedInUser ? (
          <div className="result-box">

            <h3>
              👋 Welcome, {loggedInUser.name}!
            </h3>

            <p>
              Email: {loggedInUser.email}
            </p>

            <button
              onClick={handleLogout}
            >
              Logout
            </button>

          </div>
        ) : (
          <>
            {/* REGISTER */}

            <div className="auth-box">

              <h3>📝 Register</h3>

              <form
                onSubmit={handleRegister}
              >

                <input
                  type="text"
                  placeholder="Name"
                  value={registerData.name}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      name: e.target.value,
                    })
                  }
                  required
                />

                <input
                  type="email"
                  placeholder="Email"
                  value={registerData.email}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      email: e.target.value,
                    })
                  }
                  required
                />

                <input
                  type="password"
                  placeholder="Password"
                  value={registerData.password}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      password: e.target.value,
                    })
                  }
                  required
                />

                <button type="submit">
                  Register
                </button>

              </form>

              {registerMessage && (
                <p>
                  {registerMessage}
                </p>
              )}

            </div>

            {/* LOGIN */}

            <div className="auth-box">

              <h3>🔑 Login</h3>

              <form
                onSubmit={handleLogin}
              >

                <input
                  type="email"
                  placeholder="Email"
                  value={loginData.email}
                  onChange={(e) =>
                    setLoginData({
                      ...loginData,
                      email: e.target.value,
                    })
                  }
                  required
                />

                <input
                  type="password"
                  placeholder="Password"
                  value={loginData.password}
                  onChange={(e) =>
                    setLoginData({
                      ...loginData,
                      password: e.target.value,
                    })
                  }
                  required
                />

                <button type="submit">
                  Login
                </button>

              </form>

              {loginMessage && (
                <p>
                  {loginMessage}
                </p>
              )}

            </div>
          </>
        )}

      </section>

      {/* ======================================================
          UPLOAD
      ====================================================== */}

      <section className="data-section">

        <h2>
          📂 Dataset Upload
        </h2>

        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
        />

        {file && (
          <p>
            Selected File:
            {" "}
            <strong>
              {file.name}
            </strong>
          </p>
        )}

        <button
          onClick={handleUpload}
          disabled={loading}
        >
          {loading
            ? "Uploading & Analyzing..."
            : "Upload & Analyze"}
        </button>

        <button
          onClick={() =>
            window.open(
              `${API_URL}/generate-report`,
              "_blank"
            )
          }
        >
          📄 Generate PDF Report
        </button>

      </section>

      {/* ======================================================
          DATA ANALYSIS
      ====================================================== */}

      {analysis && (
        <section className="data-section">

          <h2>
            📊 Dataset Analysis
          </h2>

          {analysis.error ? (
            <div className="result-box">
              ❌ {analysis.error}
            </div>
          ) : (
            <div className="stats-grid">

              <div className="stat-card">
                <h3>Rows</h3>
                <p>{analysis.rows}</p>
              </div>

              <div className="stat-card">
                <h3>Columns</h3>
                <p>{analysis.columns}</p>
              </div>

              <div className="stat-card">
                <h3>Missing Values</h3>
                <p>
                  {analysis.missing_values ?? 0}
                </p>
              </div>

              <div className="stat-card">
                <h3>Duplicate Rows</h3>
                <p>
                  {analysis.duplicate_rows ?? 0}
                </p>
              </div>

            </div>
          )}

        </section>
      )}

      {/* ======================================================
          DATA CLEANING
      ====================================================== */}

      {analysis && (
        <section className="data-section">

          <h2>
            🧹 Data Cleaning
          </h2>

          <p>
            Automatically handle missing values,
            duplicate records and data quality issues.
          </p>

          <button
            onClick={handleCleaning}
            disabled={cleaning}
          >
            {cleaning
              ? "Cleaning Data..."
              : "Clean Dataset"}
          </button>

          {cleaningResult && (
            <div className="result-box">

              {cleaningResult.error ? (
                <p>
                  ❌ {cleaningResult.error}
                </p>
              ) : (
                <>
                  <h3>
                    Cleaning Result
                  </h3>

                  <p>
                    Original Rows:{" "}
                    {cleaningResult.original_rows}
                  </p>

                  <p>
                    Final Rows:{" "}
                    {cleaningResult.final_rows}
                  </p>

                  <p>
                    Duplicates Removed:{" "}
                    {cleaningResult.duplicates_removed}
                  </p>

                  <p>
                    Missing Values Before:{" "}
                    {cleaningResult.missing_values_before}
                  </p>

                  <p>
                    Missing Values After:{" "}
                    {cleaningResult.missing_values_after}
                  </p>
                </>
              )}

            </div>
          )}

        </section>
      )}

      {/* ======================================================
          OUTLIERS
      ====================================================== */}

      {analysis && (
        <section className="data-section">

          <h2>
            🚨 Outlier Detection
          </h2>

          <p>
            Detect unusual values using the IQR method.
          </p>

          <button
            onClick={handleOutliers}
            disabled={outlierLoading}
          >
            {outlierLoading
              ? "Detecting Outliers..."
              : "Detect Outliers"}
          </button>

          {outlierResult && (
            <div className="result-box">

              {outlierResult.error ? (
                <p>
                  ❌ {outlierResult.error}
                </p>
              ) : (
                <pre>
                  {JSON.stringify(
                    outlierResult,
                    null,
                    2
                  )}
                </pre>
              )}

            </div>
          )}

        </section>
      )}

      {/* ======================================================
          STATISTICS
      ====================================================== */}

      {statistics && (
        <section className="data-section">

          <h2>
            📈 Statistical Analysis
          </h2>

          {statisticsLoading ? (
            <p>
              Loading statistics...
            </p>
          ) : (
            <div className="result-box">
              <pre>
                {JSON.stringify(
                  statistics,
                  null,
                  2
                )}
              </pre>
            </div>
          )}

        </section>
      )}

      {/* ======================================================
          CHART 1
      ====================================================== */}

      {chartData.length > 0 && (
        <section className="data-section">

          <h2>
            📊 Total Spending by Customer
          </h2>

          <ResponsiveContainer
            width="100%"
            height={350}
          >

            <BarChart data={chartData}>

              <CartesianGrid
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="Customer_ID"
              />

              <YAxis />

              <Tooltip />

              <Bar
                dataKey="Total_Spending"
                name="Total Spending"
              />

            </BarChart>

          </ResponsiveContainer>

        </section>
      )}

      {/* ======================================================
          CHART 2
      ====================================================== */}

      {incomeSpendingData.length > 0 && (
        <section className="data-section">

          <h2>
            💰 Monthly Income vs Total Spending
          </h2>

          <ResponsiveContainer
            width="100%"
            height={350}
          >

            <ScatterChart>

              <CartesianGrid />

              <XAxis
                type="number"
                dataKey="Monthly_Income"
                name="Monthly Income"
              />

              <YAxis
                type="number"
                dataKey="Total_Spending"
                name="Total Spending"
              />

              <ZAxis
                range={[50, 200]}
              />

              <Tooltip
                cursor={{
                  strokeDasharray: "3 3",
                }}
              />

              <Scatter
                name="Customers"
                data={incomeSpendingData}
              />

            </ScatterChart>

          </ResponsiveContainer>

        </section>
      )}

      {/* ======================================================
          CHART 3
      ====================================================== */}

      {ordersCityData.length > 0 && (
        <section className="data-section">

          <h2>
            🏙️ Orders by City
          </h2>

          <ResponsiveContainer
            width="100%"
            height={350}
          >

            <BarChart data={ordersCityData}>

              <CartesianGrid
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="City"
              />

              <YAxis />

              <Tooltip />

              <Bar
                dataKey="Orders"
                name="Orders"
              />

            </BarChart>

          </ResponsiveContainer>

        </section>
      )}

      {/* ======================================================
          CHART 4
      ====================================================== */}

      {satisfactionCityData.length > 0 && (
        <section className="data-section">

          <h2>
            ⭐ Satisfaction by City
          </h2>

          <ResponsiveContainer
            width="100%"
            height={350}
          >

            <BarChart
              data={satisfactionCityData}
            >

              <CartesianGrid
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="City"
              />

              <YAxis />

              <Tooltip />

              <Bar
                dataKey="Satisfaction"
                name="Satisfaction"
              />

            </BarChart>

          </ResponsiveContainer>

        </section>
      )}

      {/* ======================================================
          CORRELATION
      ====================================================== */}

      {correlation && (
        <section className="data-section">

          <h2>
            🔗 Correlation Analysis
          </h2>

          <div className="result-box">

            <pre>
              {JSON.stringify(
                correlation,
                null,
                2
              )}
            </pre>

          </div>

        </section>
      )}

      {/* ======================================================
          AI INSIGHTS
      ====================================================== */}

      {aiInsights.length > 0 && (
        <section className="data-section">

          <h2>
            🤖 AI-Generated Insights
          </h2>

          <div className="result-box">

            <ul>
              {aiInsights.map(
                (insight, index) => (
                  <li key={index}>
                    {insight}
                  </li>
                )
              )}
            </ul>

          </div>

        </section>
      )}
{/* ======================================================
    ANALYSIS HISTORY
====================================================== */}

{loggedInUser && history.length > 0 && (
  <section className="data-section">

    <h2>
      📜 Analysis History
    </h2>

    <div className="result-box">

      <table>
        <thead>
          <tr>
            <th>File Name</th>
            <th>Rows</th>
            <th>Columns</th>
            <th>Date</th>
          </tr>
        </thead>

        <tbody>
          {history.map((item) => (
            <tr key={item.id}>
              <td>{item.file_name}</td>
              <td>{item.rows_count}</td>
              <td>{item.columns_count}</td>
              <td>
                {new Date(
                  item.created_at
                ).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

    </div>

  </section>
)}
      {/* ======================================================
          MACHINE LEARNING
      ====================================================== */}

      {mlColumns && (
        <section className="data-section">

          <h2>
            🤖 Machine Learning
          </h2>

          <p>
            Machine learning models can classify
            customer satisfaction, predict spending,
            and group customers into clusters.
          </p>

        </section>
      )}

      {/* ======================================================
          CLASSIFICATION
      ====================================================== */}

      {mlColumns && (
        <section className="data-section">

          <h2>
            🎯 Classification
          </h2>

          <p>
            Predict whether a customer is
            Satisfied or Not Satisfied.
          </p>

          <button
            onClick={handleClassification}
            disabled={classificationLoading}
          >
            {classificationLoading
              ? "Running Classification..."
              : "Run Classification"}
          </button>

          {classificationResult && (
            <div className="result-box">

              {classificationResult.error ? (
                <p>
                  ❌ {classificationResult.error}
                </p>
              ) : (
                <>
                  <h3>
                    Classification Result
                  </h3>

                  <p>
                    <strong>Model:</strong>{" "}
                    {classificationResult.model}
                  </p>

                  <p>
                    <strong>Accuracy:</strong>{" "}
                    {classificationResult.accuracy}%
                  </p>

                  <p>
                    <strong>Training Rows:</strong>{" "}
                    {classificationResult.training_rows}
                  </p>

                  <p>
                    <strong>Testing Rows:</strong>{" "}
                    {classificationResult.testing_rows}
                  </p>
                </>
              )}

            </div>
          )}

        </section>
      )}

      {/* ======================================================
          REGRESSION
      ====================================================== */}

      {mlColumns && (
        <section className="data-section">

          <h2>
            📉 Regression Analysis
          </h2>

          <p>
            Linear Regression predicts Total Spending
            using Age, Monthly Income and Orders.
          </p>

          <button
            onClick={handleRegression}
            disabled={regressionLoading}
          >
            {regressionLoading
              ? "Running Regression..."
              : "Run Regression"}
          </button>

          {regressionResult && (
            <div className="result-box">

              {regressionResult.error ? (
                <p>
                  ❌ {regressionResult.error}
                </p>
              ) : (
                <>
                  <h3>
                    Regression Result
                  </h3>

                  <p>
                    <strong>Model:</strong>{" "}
                    {regressionResult.model}
                  </p>

                  <p>
                    <strong>Target:</strong>{" "}
                    {regressionResult.target}
                  </p>

                  <p>
                    <strong>R² Score:</strong>{" "}
                    {regressionResult.r2_score}
                  </p>

                  <p>
                    <strong>
                      Mean Squared Error:
                    </strong>{" "}
                    {regressionResult.mean_squared_error}
                  </p>

                  <p>
                    <strong>Training Rows:</strong>{" "}
                    {regressionResult.training_rows}
                  </p>

                  <p>
                    <strong>Testing Rows:</strong>{" "}
                    {regressionResult.testing_rows}
                  </p>
                </>
              )}

            </div>
          )}

        </section>
      )}

      {/* ======================================================
          PREDICTION
      ====================================================== */}

      {mlColumns && (
        <section className="data-section">

          <h2>
            🔮 Spending Prediction
          </h2>

          <p>
            Enter customer information to predict
            Total Spending.
          </p>

          <div className="prediction-form">

            <input
              type="number"
              placeholder="Age"
              value={predictionData.Age}
              onChange={(e) =>
                setPredictionData({
                  ...predictionData,
                  Age: e.target.value,
                })
              }
            />

            <input
              type="number"
              placeholder="Monthly Income"
              value={
                predictionData.Monthly_Income
              }
              onChange={(e) =>
                setPredictionData({
                  ...predictionData,
                  Monthly_Income:
                    e.target.value,
                })
              }
            />

            <input
              type="number"
              placeholder="Orders"
              value={predictionData.Orders}
              onChange={(e) =>
                setPredictionData({
                  ...predictionData,
                  Orders:
                    e.target.value,
                })
              }
            />

            <button
              onClick={handlePrediction}
              disabled={predictionLoading}
            >
              {predictionLoading
                ? "Predicting..."
                : "Predict Spending"}
            </button>

          </div>

          {predictionResult && (
            <div className="result-box">

              {predictionResult.error ? (
                <p>
                  ❌ {predictionResult.error}
                </p>
              ) : (
                <>
                  <h3>
                    🎯 Prediction Result
                  </h3>

                  <p>
                    Predicted Total Spending:
                  </p>

                  <h2>
                    ₹{" "}
                    {Number(
                      predictionResult
                        .predicted_total_spending ??
                        predictionResult.prediction ??
                        0
                    ).toFixed(2)}
                  </h2>
                </>
              )}

            </div>
          )}

        </section>
      )}

      {/* ======================================================
          CLUSTERING
      ====================================================== */}

      {mlColumns && (
        <section className="data-section">

          <h2>
            👥 Customer Clustering
          </h2>

          <p>
            K-Means clustering groups customers
            based on Age, Monthly Income, Orders
            and Total Spending.
          </p>

          <button
            onClick={handleClustering}
            disabled={clusteringLoading}
          >
            {clusteringLoading
              ? "Running Clustering..."
              : "Run Customer Clustering"}
          </button>

          {clusteringResult && (
            <div className="result-box">

              {clusteringResult.error ? (
                <p>
                  ❌ {clusteringResult.error}
                </p>
              ) : (
                <>
                  <h3>
                    Clustering Result
                  </h3>

                  <p>
                    <strong>Model:</strong>{" "}
                    {clusteringResult.model}
                  </p>

                  <p>
                    <strong>
                      Number of Clusters:
                    </strong>{" "}
                    {clusteringResult.clusters}
                  </p>

                  {Array.isArray(
                    clusteringResult.data
                  ) && (
                    <div>

                      <h4>
                        Customer Cluster Assignments
                      </h4>

                      <table>

                        <thead>
                          <tr>
                            <th>Row</th>
                            <th>Cluster</th>
                          </tr>
                        </thead>

                        <tbody>
                          {clusteringResult.data.map(
                            (item) => (
                              <tr
                                key={item.row}
                              >
                                <td>
                                  {item.row}
                                </td>

                                <td>
                                  Cluster{" "}
                                  {item.cluster}
                                </td>
                              </tr>
                            )
                          )}
                        </tbody>

                      </table>

                    </div>
                  )}

                </>
              )}

            </div>
          )}

        </section>
      )}

      {/* ======================================================
          PROJECT WORKFLOW
      ====================================================== */}

      <section className="data-section">

        <h2>
          ⚙️ Project Workflow
        </h2>

        <div className="workflow">

          <div>👤 User</div>

          <span>→</span>

          <div>🔐 Authentication</div>

          <span>→</span>

          <div>💻 React Dashboard</div>

          <span>→</span>

          <div>🐍 Flask Backend</div>

          <span>→</span>

          <div>📂 Dataset</div>

          <span>→</span>

          <div>🧹 Data Cleaning</div>

          <span>→</span>

          <div>📊 EDA</div>

          <span>→</span>

          <div>🤖 Machine Learning</div>

          <span>→</span>

          <div>🔮 Prediction</div>

          <span>→</span>

          <div>👥 Clustering</div>

        </div>

      </section>

      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer className="footer">

        <h3>
          AI-Powered Data Analytics Dashboard
        </h3>

        <p>
          B.Sc. Computer Science Final Year Project
        </p>

        <p>
          Python + Flask + React + Machine Learning
        </p>

      </footer>

    </div>
  );
}

export default App;