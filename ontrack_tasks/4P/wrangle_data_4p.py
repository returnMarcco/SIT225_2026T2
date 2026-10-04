import firebase_admin
from firebase_admin import credentials, db
import pandas as pd


# -------------------------
# 1. Connect to Firebase
# -------------------------

DATABASE_URL = ""

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": DATABASE_URL
})


# -------------------------
# 2. Fetch Firebase data
# -------------------------

data = db.reference("movement_events").get()

df = pd.DataFrame.from_dict(
    data,
    orient="index"
)

df.index.name = "firebase_id"

df = df.reset_index()


# -------------------------
# 3. Clean / validate data
# -------------------------

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True,
    errors="coerce"
)

required_columns = [
    "movement",
    "sensor_id",
    "timestamp",
    "image_base64"
]

if df[required_columns].isnull().any().any():
    raise ValueError(
        "Missing values found in required columns"
    )

if df.duplicated().any():
    raise ValueError(
        "Duplicate rows found"
    )

if not df["movement"].isin([0, 1]).all():
    raise ValueError(
        "Invalid movement values found"
    )

df = (
    df.sort_values("timestamp")
    .reset_index(drop=True)
)


# -------------------------
# 4. Create simulated year
# -------------------------

real_start = df["timestamp"].min()
real_end = df["timestamp"].max()


simulated_start = pd.Timestamp(
    "2026-01-01 00:00:00",
    tz="UTC"
)

simulated_end = pd.Timestamp(
    "2026-12-31 23:59:59",
    tz="UTC"
)


real_duration = (
    real_end - real_start
).total_seconds()


simulated_duration = (
    simulated_end - simulated_start
).total_seconds()


def convert_to_simulated_time(timestamp):

    elapsed_real = (
        timestamp - real_start
    ).total_seconds()

    proportion = (
        elapsed_real / real_duration
    )

    elapsed_simulated = (
        proportion * simulated_duration
    )

    return (
        simulated_start
        + pd.Timedelta(
            seconds=elapsed_simulated
        )
    )


df["simulated_timestamp"] = (
    df["timestamp"]
    .apply(convert_to_simulated_time)
)


# -------------------------
# 5. Add simulated variables
# -------------------------

df["simulated_date"] = (
    df["simulated_timestamp"]
    .dt.date
)

df["simulated_month"] = (
    df["simulated_timestamp"]
    .dt.month
)

df["simulated_hour"] = (
    df["simulated_timestamp"]
    .dt.hour
)

df["simulated_day_of_week"] = (
    df["simulated_timestamp"]
    .dt.day_name()
)


# -------------------------
# 6. Determine Australian season
# -------------------------

def get_season(month):

    if month in [12, 1, 2]:
        return "Summer"

    elif month in [3, 4, 5]:
        return "Autumn"

    elif month in [6, 7, 8]:
        return "Winter"

    else:
        return "Spring"


df["simulated_season"] = (
    df["simulated_month"]
    .apply(get_season)
)


# -------------------------
# 7. Warm vs cool periods
# -------------------------

df["season_group"] = (
    df["simulated_season"]
    .replace({
        "Summer": "Warmer",
        "Spring": "Warmer",
        "Autumn": "Cooler",
        "Winter": "Cooler"
    })
)


# -------------------------
# 8. Time between detections
# -------------------------

df["time_since_previous"] = (
    df["timestamp"]
    .diff()
)


# -------------------------
# 9. Mark real event rows
# -------------------------

df["record_type"] = "event"


# -------------------------
# 10. Create all simulated dates
# -------------------------

all_dates = pd.DataFrame({
    "simulated_date": pd.date_range(
        start="2026-01-01",
        end="2026-12-31",
        freq="D"
    ).date
})


# -------------------------
# 11. Find nights with no events
# -------------------------

existing_dates = set(
    df["simulated_date"]
)

zero_dates = all_dates[
    ~all_dates["simulated_date"]
    .isin(existing_dates)
].copy()


# -------------------------
# 12. Populate zero-event rows
# -------------------------

zero_dates["firebase_id"] = None

zero_dates["image_base64"] = None

zero_dates["movement"] = 0

zero_dates["sensor_id"] = "PIR_CAM_01"

zero_dates["timestamp"] = pd.NaT

zero_dates["simulated_timestamp"] = pd.NaT


zero_dates["simulated_month"] = (
    pd.to_datetime(
        zero_dates["simulated_date"]
    )
    .dt.month
)


zero_dates["simulated_hour"] = None


zero_dates["simulated_day_of_week"] = (
    pd.to_datetime(
        zero_dates["simulated_date"]
    )
    .dt.day_name()
)


zero_dates["simulated_season"] = (
    zero_dates["simulated_month"]
    .apply(get_season)
)


zero_dates["season_group"] = (
    zero_dates["simulated_season"]
    .replace({
        "Summer": "Warmer",
        "Spring": "Warmer",
        "Autumn": "Cooler",
        "Winter": "Cooler"
    })
)


zero_dates["time_since_previous"] = pd.NaT

zero_dates["record_type"] = "zero_event"


# -------------------------
# 13. Combine real events
#     and zero-event nights
# -------------------------

df = pd.concat(
    [
        df,
        zero_dates
    ],
    ignore_index=True
)


# -------------------------
# 14. Sort by simulated date
# -------------------------

df = (
    df.sort_values(
        [
            "simulated_date",
            "simulated_timestamp"
        ],
        na_position="last"
    )
    .reset_index(drop=True)
)


# -------------------------
# 15. Export wrangled dataset
# -------------------------

df.to_csv(
    "movement_events_simulated.csv",
    index=False
)


# -------------------------
# 16. Basic checks
# -------------------------

print("Total rows:")
print(len(df))


print("\nReal movement events:")
print(
    (df["record_type"] == "event").sum()
)


print("\nZero-event nights:")
print(
    (df["record_type"] == "zero_event").sum()
)


print("\nTotal simulated dates:")
print(
    df["simulated_date"]
    .nunique()
)


print("\nDetections by simulated season:")

season_counts = (
    df.groupby(
        "simulated_season"
    )["movement"]
    .sum()
)

print(season_counts)


print("\nWarmer vs cooler periods:")

warm_cool_counts = (
    df.groupby(
        "season_group"
    )["movement"]
    .sum()
)

print(warm_cool_counts)