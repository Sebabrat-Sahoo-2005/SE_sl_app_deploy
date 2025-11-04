import os
import pandas as pd
import numpy as np
import joblib
import optuna
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

DATA_PATH = r"C:\Users\vaibh\OneDrive\Desktop\kdd\nsl-kdd\KDDTest+.txt"
HAS_DIFFICULTY_COL = True

feature_names = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes","land",
    "wrong_fragment","urgent","hot","num_failed_logins","logged_in","num_compromised",
    "root_shell","su_attempted","num_root","num_file_creations","num_shells",
    "num_access_files","num_outbound_cmds","is_host_login","is_guest_login","count",
    "srv_count","serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate",
    "same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count",
    "dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate","dst_host_serror_rate",
    "dst_host_srv_serror_rate","dst_host_rerror_rate","dst_host_srv_rerror_rate"
]

cols = feature_names + ["label"]
if HAS_DIFFICULTY_COL:
    cols.append("difficulty")

print("Loading data from:", DATA_PATH)
df = pd.read_csv(DATA_PATH, names=cols, header=None)

if "difficulty" in df.columns:
    df = df.drop(columns=["difficulty"])

df["is_attack"] = (df["label"].astype(str).str.lower() != "normal").astype(int)
print("Label count:\n", df["is_attack"].value_counts())

categorical_cols = ["protocol_type", "service", "flag"]
numeric_cols = [c for c in feature_names if c not in categorical_cols]
df[numeric_cols] = df[numeric_cols].fillna(0).astype(float)

X = df[feature_names].copy()
y = df["is_attack"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=41
)

numeric_transformer = Pipeline(steps=[
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_cols),
    ("cat", categorical_transformer, categorical_cols)
])

def objective(trial):
    model_choice = trial.suggest_categorical("model", ["random_forest"])
    
    if model_choice == "random_forest":
        n_estimators = trial.suggest_int("n_estimators", 50, 300)
        max_depth = trial.suggest_int("max_depth", 5, 30)
        clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    
    pipe = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])
    scores = cross_val_score(pipe, X_train, y_train, cv=3, scoring="accuracy", n_jobs=-1)
    return np.mean(scores)

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)

print("Best trial:", study.best_trial.params)

best_params = study.best_trial.params
best_model_choice = best_params.pop("model")

if best_model_choice == "random_forest":
    final_model = RandomForestClassifier(**best_params, random_state=42)


final_pipe = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", final_model)])
final_pipe.fit(X_train, y_train)
y_pred = final_pipe.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save the trained pipeline to a file
model_path = r"C:\Users\vaibh\OneDrive\Desktop\kdd\final_pipeline.pkl"
joblib.dump(final_pipe, model_path)
print(f"Trained pipeline saved to: {model_path}")

# To load it later
# loaded_pipe = joblib.load(model_path)
# y_pred_loaded = loaded_pipe.predict(X_test)
