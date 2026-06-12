import mysql.connector
import pandas as pd 
from sklearn.preprocessing import LabelEncoder

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mr.abhi1149",
    database="patients"
)

cursor = conn.cursor()

df = pd.read_sql("select * from covid_toy", conn)

print(df)

df["fever"] = df["fever"].fillna(df["fever"].mean())

le = LabelEncoder()
df['gender'] = le.fit_transform(df['gender'])
df['cough'] = le.fit_transform(df['cough'])
df['city'] = le.fit_transform(df['city'])
df['has_covid'] = le.fit_transform(df['has_covid'])

x = df.drop(columns=['has_covid'])
y = df['has_covid']

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42)

from sklearn.neighbors import KNeighborsClassifier
kn = KNeighborsClassifier(n_neighbors=3)

kn.fit(x_train, y_train)

y_pred = kn.predict(x_test)

from sklearn.metrics import accuracy_score
print(accuracy_score(y_test, y_pred))

import joblib

joblib.dump(kn, 'kn_model.pkl')