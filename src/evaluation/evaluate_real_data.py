import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# NSL-KDD official column names (41 features + label + difficulty)
columns = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes","land",
    "wrong_fragment","urgent","hot","num_failed_logins","logged_in","num_compromised",
    "root_shell","su_attempted","num_root","num_file_creations","num_shells",
    "num_access_files","num_outbound_cmds","is_host_login","is_guest_login","count",
    "srv_count","serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate",
    "same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count",
    "dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate","dst_host_serror_rate",
    "dst_host_srv_serror_rate","dst_host_rerror_rate","dst_host_srv_rerror_rate",
    "label","difficulty"
]

# Step 1: Load train and test sets
train_df = pd.read_csv("data/external/KDDTrain+.txt", header=None, names=columns)
test_df = pd.read_csv("data/external/KDDTest+.txt", header=None, names=columns)

# Step 2: Convert label to binary — "normal" = 0, anything else (attack type) = 1
train_df["binary_label"] = train_df["label"].apply(lambda x: 0 if x == "normal" else 1)
test_df["binary_label"] = test_df["label"].apply(lambda x: 0 if x == "normal" else 1)

# Step 3: Encode categorical columns (protocol_type, service, flag)
categorical_cols = ["protocol_type", "service", "flag"]
for col in categorical_cols:
    le = LabelEncoder()
    # fit on combined train+test values so unseen categories don't break it
    le.fit(pd.concat([train_df[col], test_df[col]]))
    train_df[col] = le.transform(train_df[col])
    test_df[col] = le.transform(test_df[col])

# Step 4: Prepare features and labels
feature_cols = columns[:-2]  # everything except label and difficulty
X_train = train_df[feature_cols]
y_train = train_df["binary_label"]
X_test = test_df[feature_cols]
y_test = test_df["binary_label"]

# Step 5: Train a fresh Random Forest (same algorithm as original project)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 6: Predict and evaluate
y_pred = model.predict(X_test)

precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1-score: {f1:.3f}")

# Step 7: Confusion matrix image
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Benign', 'Attack'], yticklabels=['Benign', 'Attack'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix — NSL-KDD Validation')
plt.savefig('docs/screenshots/confusion_matrix_nslkdd.png')
print("Confusion matrix saved to docs/screenshots/confusion_matrix_nslkdd.png")

# Step 8: Simple rule-based baseline (no ML) — flag as attack if failed logins > 0 OR wrong_fragment > 0
def rule_based_baseline(row):
    if row["num_failed_logins"] > 0 or row["wrong_fragment"] > 0 or row["urgent"] > 0:
        return 1
    return 0

y_pred_baseline = test_df.apply(rule_based_baseline, axis=1)

baseline_precision = precision_score(y_test, y_pred_baseline)
baseline_recall = recall_score(y_test, y_pred_baseline)
baseline_f1 = f1_score(y_test, y_pred_baseline)

print("\n--- Rule-Based Baseline (No ML) ---")
print(f"Precision: {baseline_precision:.3f}")
print(f"Recall: {baseline_recall:.3f}")
print(f"F1-score: {baseline_f1:.3f}")