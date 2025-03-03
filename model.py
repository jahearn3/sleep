import pandas as pd
import process_data
import seaborn as sns
import matplotlib.pyplot as plt


df = process_data.process_data(filename="sleep.csv")

# Discard rows with missing data
df = df.dropna()

# Encode the target variable
# df['rating_encoded'] = df['rating_smartwatch'].map({'Good': 2, 'Fair': 1, 'Poor': 0})

# One-hot encode the 'day_of_week' column
df = pd.get_dummies(df, columns=['day_of_week'], drop_first=True)  # drop_first to avoid multicollinearity


# Convert 'duration_smartwatch' from "HH:MM" to total minutes
def convert_to_minutes(duration):
    if pd.isna(duration) or duration == "":
        return 0  # Handle missing or empty values
    hours, minutes = map(int, duration.split(':'))
    return hours * 60 + minutes


df['duration_minutes'] = df['duration_smartwatch'].apply(convert_to_minutes)

# Convert hour finished eating/screentime by to time interval between eating/screentime and sleep time
df['hours_between_eat_and_sleep'] = 12 + df['start_time_hr'] - df['hour_finished_eating_by']
df['hours_between_screen_and_sleep'] = 12 + df['start_time_hr'] - df['hour_finished_screen_time_by']

# Drop columns
df = df.drop(columns=[
    'date',
    'start',
    'stop',
    'start_raw',
    'stop_raw',
    'duration_smartwatch',
    'rating_smartwatch',
    'melatonin',
    'hour_finished_eating_by',
    'hour_finished_screen_time_by',
    ])

# Compute the correlation matrix
correlation_matrix = df.corr()

# Visualize the correlation matrix
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f",
            cmap='coolwarm', vmin=-1, vmax=1, center=0,
            square=True, cbar_kws={"shrink": .8})
plt.title('Feature Correlation Matrix')
plt.savefig('feature_correlation_matrix.png',  bbox_inches='tight')
plt.clf()

# Extract correlations with the target variable
target_correlation = correlation_matrix['score_smartwatch'].drop('score_smartwatch')  # Drop self-correlation
print("Correlations with score_smartwatch:")
print(target_correlation.sort_values(ascending=False))
