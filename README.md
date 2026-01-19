# Project SAMARTH
### Systemic Aadhaar Monitoring And Resilience Tracking Hub

Project SAMARTH is a prescriptive analytics ecosystem developed for the UIDAI Data Hackathon. It is designed to move beyond traditional volume-based reporting toward a framework of systemic resilience. By analyzing raw transactional patterns, SAMARTH identifies operational friction, infrastructure instability, and regional service deserts.

---

## The IRE Framework
The project is built upon the Identity Resilience Engine (IRE) framework, which evaluates the Aadhaar ecosystem across three distinct pillars:

### 1. NEEV (Foundation)
**National Enrolment and Evaluation Vertical**
* **Metric:** Mandatory Biometric Compliance Index (MBCI).
* **Concept:** This pillar monitors the age 5-17 cohort to ensure mandatory biometric updates are completed. It identifies districts where children are at high risk of authentication failure due to outdated data.
* **Math:** Uses percentile ranking of update-to-enrolment ratios to identify relative laggards across the country.

### 2. GATI (Speed)
**Governance And Throughput Index**
* **Metric:** Administrative Load Velocity (ALV).
* **Concept:** Measures the stability of data flow. It specifically targets "Batch Dumping" behavior—where operators hoard data offline and sync in massive spikes—which threatens server stability.
* **Math:** Derived from the standard deviation of daily upload volumes. High volatility results in a lower GATI score.

### 3. NYAY (Justice)
**Network Yield and Accessibility Yardstick**
* **Metric:** Spatial Equity Coefficient (SEC).
* **Concept:** Measures the fairness of service distribution. It identifies "Service Deserts" where Aadhaar centers are concentrated in urban hubs, forcing rural residents to travel long distances.
* **Math:** Calculated using Gini-coefficient logic applied to pincode-level transaction volumes.

---

## The SAMARTH Score
The final resilience score is a weighted average that balances these three priorities:

**Formula:**
SAMARTH Score = (0.4 * NEEV) + (0.3 * GATI) + (0.3 * NYAY)

* **40% NEEV:** Prioritized because biometric expiration leads to immediate service denial.
* **30% GATI:** Ensures infrastructure health and prevents server timeouts.
* **30% NYAY:** Focuses on social justice and last-mile accessibility.

---

## Technical Stack
* **Language:** Python 3.9+
* **Interface:** Streamlit (Governance Cockpit)
* **Data Handling:** Pandas, NumPy
* **Visualization:** Plotly Express

---

## Installation and Usage

### 1. Clone the Repository
```bash
git clone https://github.com/GauravBarwa/UIDAI-Hackathon.git
cd uidai-hackathon
pip install -r requirements.txt
```
### 2. Run the Application
```bash
streamlit run app.py
```
_The app will automatically open in your default browser at http://localhost:8501._

---
## Data Pipeline
If you wish to re-run the analysis from raw data:

1. **Phase 1 (Cleaning):**
   Run the cleaning script to standardize mismatched state and district names using a strict "Force Model":
   ```bash
   python final_clean.py
   ```
2. **Phase 2 (Analytics):**
Run the metrics calculation script to mine raw data and calculate NEEV, GATI, and NYAY scores:
   ```bash
   python calculate_metrics.py
   ```
3. **Phase 3 (Visualization):**
The generated output file aadhaar_hackathon_final_dashboard.csv is automatically consumed by the main application:
   ```bash
   streamlit run app.py
   ```
---
## Features
* **National Heatmap:** A hierarchical treemap visualizing resilience scores from State down to District levels.
* **Deep-Dive Diagnostics:** Dedicated analytic tabs for NEEV, GATI, and NYAY containing specific insights and actionable recommendations (e.g., deploying mobile vans or school camps).
* **What-If Simulator:** A floating simulation panel allowing administrators to project the impact of policy interventions on regional scores in real-time.

---

## Decision Support
For every insight generated, SAMARTH provides a specific, operational recommendation:

* **Low NEEV:** Directs the District Magistrate to deploy School Saturation Camps.
* **Low GATI:** Flags the need for Daily Sync Protocols to stabilize server load.
* **Low NYAY:** Identifies specific coordinates for Mobile Aadhaar Van deployment.

---

**Developed for UIDAI Hackathon 2026** | Team ID: UIDAI_4137
   

