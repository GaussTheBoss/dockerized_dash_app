import pickle
import pandas
import numpy


def init() -> None:
    """
    A function to load the trained model artifact (.pickle) as a glocal variable.
    The model will be used by other functions to produce predictions.
    """

    global logreg_classifier
    # load pickled logistic regression model
    logreg_classifier = pickle.load(open("/app/data/logreg_classifier.pickle", "rb"))


def score(data: dict) -> dict:
    """
    A function to predict loan default/pay-off, given a loan application sample (record).

    Args:
        data (dict): input dictionary to be scored, containing predictive features.

    Returns:
        (dict): Scored (predicted) input data.
    """

    # Turn input data into a 1-record DataFrame
    data = pandas.DataFrame([data])

    # There are only two unique values in data.number_people_liable.
    # Treat it as a categorical feature, to mimic training process
    data.number_people_liable = data.number_people_liable.astype("category")

    # Alternitavely, these features can be saved (pickled) and re-loaded
    predictive_features = sorted(
        [
            "checking_status",
            "credit_amount",
            "credit_history",
            "debtors_guarantors",
            "duration_months",
            "foreign_worker",
            "housing",
            "installment_plans",
            "installment_rate",
            "job",
            "number_existing_credits",
            "number_people_liable",
            "present_employment_since",
            "present_residence_since",
            "property",
            "purpose",
            "savings_account",
            "telephone",
        ]
    )

    # Predict using saved model
    probability = numpy.round(
        logreg_classifier.predict_proba(data[predictive_features])[0][1], 3
    )

    data["probability_of_default"] = probability

    data["predicted_score"] = "Default" if probability > 0.5 else "Pay-Off"

    return data.to_dict(orient="records")[0]
