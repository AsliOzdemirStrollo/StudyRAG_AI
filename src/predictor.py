from sklearn.linear_model import LinearRegression
import numpy as np


# ---------------------------------------------------
# Synthetic training dataset
# ---------------------------------------------------

X = np.array([

    [55, 2, 3, 40, 50, 120, 180],
    [60, 5, 6, 55, 60, 90, 140],
    [72, 7, 10, 70, 75, 70, 100],
    [80, 10, 14, 85, 90, 50, 80],
    [90, 14, 20, 95, 100, 40, 60],

    [50, 1, 2, 35, 40, 150, 220],
    [65, 4, 5, 60, 55, 100, 150],
    [75, 8, 12, 78, 80, 60, 90],
    [85, 12, 16, 90, 95, 45, 70],
    [92, 15, 22, 98, 100, 30, 50],
])

y = np.array([
    50,
    58,
    72,
    84,
    94,

    45,
    63,
    77,
    88,
    96
])


# ---------------------------------------------------
# Train model
# ---------------------------------------------------

model = LinearRegression()

model.fit(X, y)


# ---------------------------------------------------
# Prediction Function
# ---------------------------------------------------

def predict_exam_score(
    previous_score,
    days_left,
    study_hours,
    quiz_score,
    completion_percent,
    document_pages,
    document_chunks
):

    # -----------------------------------
    # Base score
    # -----------------------------------

    predicted_score = previous_score * 0.35

    # -----------------------------------
    # Quiz accuracy impact
    # -----------------------------------

    effective_quiz_score = quiz_score * (completion_percent / 100)
    predicted_score += effective_quiz_score * 0.40

    # -----------------------------------
    # Quiz completion impact
    # -----------------------------------

    predicted_score += completion_percent * 0.10

    # -----------------------------------
    # Study hours impact
    # -----------------------------------

    predicted_score += min(
        study_hours * 1.2,
        15
    )

    # -----------------------------------
    # Days left impact
    # -----------------------------------

    predicted_score += min(
        days_left * 0.8,
        10
    )

    # -----------------------------------
    # Long document penalty
    # -----------------------------------

    if document_pages > 100:

        predicted_score -= 8

    elif document_pages > 70:

        predicted_score -= 4

    # -----------------------------------
    # Chunk complexity penalty
    # -----------------------------------

    if document_chunks > 180:

        predicted_score -= 5

    # -----------------------------------
    # Final cleanup
    # -----------------------------------

    predicted_score = round(
        predicted_score,
        1
    )

    predicted_score = max(
        0,
        min(100, predicted_score)
    )

    return predicted_score


# ---------------------------------------------------
# Explainable AI Feedback
# ---------------------------------------------------

def generate_prediction_feedback(
    predicted_score,
    quiz_score,
    days_left,
    study_hours,
    document_pages
):

    feedback = []

    # Quiz performance

    if quiz_score >= 80:

        feedback.append(
            "✅ Strong quiz performance is improving the prediction."
        )

    elif quiz_score < 50:

        feedback.append(
            "⚠️ Low quiz accuracy is reducing the prediction."
        )

    # Study time

    if study_hours >= 15:

        feedback.append(
            "✅ Planned study time is strong."
        )

    elif study_hours < 5:

        feedback.append(
            "⚠️ Limited study hours may affect performance."
        )

    # Remaining time

    if days_left <= 2:

        feedback.append(
            "⚠️ Very limited time remains before the exam."
        )

    elif days_left >= 10:

        feedback.append(
            "✅ Good amount of preparation time remains."
        )

    # Document length

    if document_pages >= 100:

        feedback.append(
            "⚠️ The study document is quite long."
        )

    elif document_pages <= 40:

        feedback.append(
            "✅ The document length is manageable."
        )

    # Overall prediction

    if predicted_score >= 85:

        feedback.append(
            "🎯 Overall prediction is very strong."
        )

    elif predicted_score < 60:

        feedback.append(
            "📚 Additional revision is recommended."
        )

    return feedback