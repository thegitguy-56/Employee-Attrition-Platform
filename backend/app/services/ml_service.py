import os, json, joblib, uuid
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

ML_MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models"))

_models = {"logistic_regression": None, "decision_tree": None, "random_forest": None}
_scaler = None
_label_encoders = None
_feature_columns = None
_feature_importance = None


def load_models():
    global _models, _scaler, _label_encoders, _feature_columns, _feature_importance
    logger.info(f"Loading ML models from: {ML_MODELS_DIR}")
    for name in _models:
        path = os.path.join(ML_MODELS_DIR, f"{name}.pkl")
        if os.path.exists(path):
            _models[name] = joblib.load(path)
            logger.info(f"  loaded {name}")
        else:
            logger.warning(f"  missing {path}")
    for fname, attr in [("scaler.pkl","_scaler"),("label_encoders.pkl","_label_encoders"),("feature_columns.pkl","_feature_columns")]:
        p = os.path.join(ML_MODELS_DIR, fname)
        if os.path.exists(p):
            globals()[attr] = joblib.load(p)
    fi_path = os.path.join(ML_MODELS_DIR, "feature_importance.json")
    if os.path.exists(fi_path):
        with open(fi_path) as f:
            _feature_importance = json.load(f)


def _preprocess_employee(emp: Dict[str, Any]) -> np.ndarray:
    if _scaler is None or _feature_columns is None:
        raise ValueError("ML artifacts not loaded.")
    field_map = {
        "age":"Age","business_travel":"BusinessTravel","distance_from_home":"DistanceFromHome",
        "education":"Education","education_field":"EducationField",
        "environment_satisfaction":"EnvironmentSatisfaction","gender":"Gender",
        "job_involvement":"JobInvolvement","job_level":"JobLevel","job_role":"JobRole",
        "job_satisfaction":"JobSatisfaction","marital_status":"MaritalStatus",
        "monthly_income":"MonthlyIncome","num_companies_worked":"NumCompaniesWorked",
        "overtime":"OverTime","percent_salary_hike":"PercentSalaryHike",
        "performance_rating":"PerformanceRating","relationship_satisfaction":"RelationshipSatisfaction",
        "stock_option_level":"StockOptionLevel","total_working_years":"TotalWorkingYears",
        "training_times_last_year":"TrainingTimesLastYear","work_life_balance":"WorkLifeBalance",
        "years_at_company":"YearsAtCompany","years_in_current_role":"YearsInCurrentRole",
        "years_since_last_promotion":"YearsSinceLastPromotion","years_with_curr_manager":"YearsWithCurrManager",
        "department":"Department",
    }
    defaults = {
        "Age":35,"BusinessTravel":"Travel_Rarely","DistanceFromHome":10,"Education":3,
        "EducationField":"Life Sciences","EnvironmentSatisfaction":3,"Gender":"Male",
        "JobInvolvement":3,"JobLevel":2,"JobRole":"Sales Executive","JobSatisfaction":3,
        "MaritalStatus":"Single","MonthlyIncome":5000,"NumCompaniesWorked":2,"OverTime":"No",
        "PercentSalaryHike":14,"PerformanceRating":3,"RelationshipSatisfaction":3,
        "StockOptionLevel":0,"TotalWorkingYears":10,"TrainingTimesLastYear":3,
        "WorkLifeBalance":3,"YearsAtCompany":5,"YearsInCurrentRole":3,
        "YearsSinceLastPromotion":1,"YearsWithCurrManager":3,"Department":"Research & Development",
    }
    row = {dataset_key: emp.get(api_key, defaults.get(dataset_key, 0))
           for api_key, dataset_key in field_map.items()}
    df = pd.DataFrame([row])
    cat_cols = ["BusinessTravel","Department","EducationField","Gender","JobRole","MaritalStatus","OverTime"]
    if _label_encoders:
        for col in cat_cols:
            if col in df.columns and col in _label_encoders:
                try:
                    df[col] = _label_encoders[col].transform(df[col].astype(str))
                except ValueError:
                    df[col] = 0
    for c in _feature_columns:
        if c not in df.columns:
            df[c] = 0
    return _scaler.transform(df[_feature_columns])


def _risk_level(s): return "High" if s>=0.7 else ("Medium" if s>=0.4 else "Low")
def _confidence(s): d=abs(s-0.5); return "High" if d>=0.3 else ("Medium" if d>=0.15 else "Low")


def generate_recommendation(risk_score: float, emp: Dict) -> str:
    tips = []
    if str(emp.get("overtime","No")).lower()=="yes":  tips.append("High overtime — review workload.")
    if int(emp.get("job_satisfaction",3))<=2:          tips.append("Low job satisfaction — schedule 1-on-1.")
    if int(emp.get("work_life_balance",3))<=2:         tips.append("Poor work-life balance — consider flexible hours.")
    if float(emp.get("monthly_income",5000))<3000:     tips.append("Below-average pay — review compensation.")
    if int(emp.get("years_since_last_promotion",0))>=4:tips.append("No promotion in 4+ years — discuss career growth.")
    pct = risk_score*100
    prefix = f"Risk: {pct:.1f}% — "
    if tips: return prefix + " | ".join(tips)
    if pct>=70: return prefix+"High risk. Schedule immediate retention conversation."
    if pct>=40: return prefix+"Moderate risk. Monitor engagement closely."
    return prefix+"Low risk. Continue regular check-ins."


def _key_factors(emp: Dict) -> List[Dict]:
    factors=[]
    checks=[
        ("overtime","Yes","high","Overtime significantly raises attrition risk"),
        ("job_satisfaction",2,"high","Low job satisfaction is a strong predictor"),
        ("work_life_balance",2,"high","Poor work-life balance leads to burnout"),
        ("environment_satisfaction",2,"medium","Low environment satisfaction"),
        ("years_since_last_promotion",4,"medium","No recent promotion"),
        ("monthly_income",3000,"high","Below-average compensation"),
        ("distance_from_home",25,"low","Long commute"),
    ]
    for field,threshold,impact,desc in checks:
        v = emp.get(field)
        if v is None: continue
        if field=="overtime" and str(v).lower()=="yes": pass
        elif field in ["job_satisfaction","work_life_balance","environment_satisfaction"] and int(v)>threshold: continue
        elif field=="years_since_last_promotion" and int(v)<threshold: continue
        elif field=="monthly_income" and float(v)>=threshold: continue
        elif field=="distance_from_home" and int(v)<threshold: continue
        factors.append({"factor":field.replace("_"," ").title(),"value":v,"impact":impact,"description":desc})
    return factors[:5]


def predict_single(emp: Dict, model_name: str="all") -> Dict:
    processed = _preprocess_employee(emp)
    names = {"logistic_regression":"Logistic Regression","decision_tree":"Decision Tree","random_forest":"Random Forest"}
    to_run = list(_models.keys()) if model_name=="all" else [model_name]
    results, scores = [], []
    for name in to_run:
        m = _models.get(name)
        if not m: continue
        proba = m.predict_proba(processed)[0]
        rs = float(proba[1]) if len(proba)>1 else float(proba[0])
        scores.append(rs)
        results.append({"model_name":names.get(name,name),"prediction":"Yes" if rs>=0.5 else "No",
                         "risk_score":round(rs,4),"risk_percentage":round(rs*100,1),"confidence":_confidence(rs)})
    if not scores: raise ValueError("No models available.")
    overall = float(np.mean(scores))
    return {"overall_prediction":"Yes" if overall>=0.5 else "No","overall_risk_score":round(overall,4),
            "risk_level":_risk_level(overall),"model_results":results,
            "key_risk_factors":_key_factors(emp),"recommendation":generate_recommendation(overall,emp)}


def predict_batch(df: pd.DataFrame) -> List[Dict]:
    results=[]
    rename={k:k.lower() for k in df.columns}
    rename.update({"OverTime":"overtime","MonthlyIncome":"monthly_income","JobSatisfaction":"job_satisfaction",
                   "WorkLifeBalance":"work_life_balance","YearsAtCompany":"years_at_company","Age":"age",
                   "Department":"department","JobRole":"job_role","Gender":"gender",
                   "MaritalStatus":"marital_status","Education":"education","DistanceFromHome":"distance_from_home",
                   "TotalWorkingYears":"total_working_years","YearsSinceLastPromotion":"years_since_last_promotion",
                   "EnvironmentSatisfaction":"environment_satisfaction"})
    for idx,row in df.iterrows():
        emp={rename.get(k,k.lower()):v for k,v in row.to_dict().items()}
        name=str(row.get("Name",row.get("EmployeeName",f"Row {idx+1}")))
        try:
            r=predict_single(emp)
            results.append({"row_number":idx+1,"employee_name":name,"overall_prediction":r["overall_prediction"],
                             "risk_score":r["overall_risk_score"],"risk_level":r["risk_level"],
                             "recommendation":r["recommendation"],"error":None})
        except Exception as e:
            results.append({"row_number":idx+1,"employee_name":name,"overall_prediction":"Error",
                             "risk_score":0.0,"risk_level":"Unknown","recommendation":"","error":str(e)})
    return results


def get_feature_importance() -> List[Dict]:
    return _feature_importance or []


def models_loaded() -> bool:
    return all(m is not None for m in _models.values())
