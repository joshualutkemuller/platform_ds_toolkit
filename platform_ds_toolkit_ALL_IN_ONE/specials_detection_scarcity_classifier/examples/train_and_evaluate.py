
import pandas as pd
from specials_classifier.model import SpecialsClassifier
from specials_classifier.features import FEATURE_COLUMNS

df = pd.read_csv("../data/sample_specials_data.csv", parse_dates=["date"])

train = df[df["date"] < "2024-01-01"]
test = df[df["date"] >= "2024-01-01"]

clf = SpecialsClassifier(C=0.5)
clf.fit(train[FEATURE_COLUMNS], train["is_special"])

metrics = clf.evaluate(test[FEATURE_COLUMNS], test["is_special"])
print(metrics)

test["special_prob"] = clf.predict_proba(test[FEATURE_COLUMNS])
print(test[["date", "special_prob"]].head())
