import plotly.express as px


def fraud_pie_chart(df):
    counts = df["Class"].value_counts().reset_index()
    counts.columns = ["Transaction", "Count"]

    counts["Transaction"] = counts["Transaction"].replace({
        0: "Genuine",
        1: "Fraud"
    })

    return px.pie(
        counts,
        names="Transaction",
        values="Count",
        hole=0.55,
        title="Fraud vs Genuine Transactions"
    )


def amount_histogram(df):
    return px.histogram(
        df,
        x="Amount",
        nbins=50,
        title="Transaction Amount Distribution"
    )


def time_chart(df):
    sample = df.head(5000)

    return px.line(
        sample,
        x="Time",
        y="Amount",
        title="Transaction Timeline"
    )