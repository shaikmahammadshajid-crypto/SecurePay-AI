import streamlit as st
import shap
import matplotlib.pyplot as plt



def get_explainer(model):
    return shap.TreeExplainer(model)


def show_shap_explanation(model, input_df):
    st.success("✅ SHAP function is running")

    """
    Display SHAP feature importance for a single prediction.
    """

    try:

        explainer = get_explainer(model)

        shap_values = explainer.shap_values(input_df)

        st.divider()
        st.subheader("🧠 Explainable AI")
        st.caption("Feature contribution towards this prediction.")

        fig = plt.figure(figsize=(10, 6))

        # Handle different SHAP versions
        if isinstance(shap_values, list):
            values = shap_values[1][0]

        elif len(shap_values.shape) == 3:
            values = shap_values[0, :, 1]

        else:
            values = shap_values[0]

        shap.plots.bar(
            shap.Explanation(
                values=values,
                base_values=explainer.expected_value,
                data=input_df.iloc[0],
                feature_names=input_df.columns,
            ),
            show=False,
        )

        st.pyplot(fig)

        plt.close(fig)

    except Exception as e:
        st.error(f"SHAP Error: {e}")