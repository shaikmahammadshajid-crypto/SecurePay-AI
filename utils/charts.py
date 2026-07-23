import plotly.graph_objects as go


def fraud_gauge(probability):
    """
    Returns a Plotly gauge chart for fraud probability.
    """

    probability = probability * 100

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=probability,
            number={"suffix": "%"},
            title={
                "text": "Fraud Probability",
                "font": {"size": 24},
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "thickness": 0.3
                },
                "steps": [
                    {
                        "range": [0, 30],
                        "color": "#4CAF50",
                    },
                    {
                        "range": [30, 60],
                        "color": "#FFC107",
                    },
                    {
                        "range": [60, 85],
                        "color": "#FF9800",
                    },
                    {
                        "range": [85, 100],
                        "color": "#F44336",
                    },
                ],
            },
        )
    )

    fig.update_layout(
        height=350,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    return fig