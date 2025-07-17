import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.metrics import accuracy_score, classification_report
from tokenizers import Tokenizer
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import WordNetLemmatizer
from transformers import (
    RobertaTokenizer,
    RobertaForSequenceClassification,
)
import torch


def reddit_dtypes(df):
    """
    Converts columns in the DataFrame to the 'category' dtype based on patterns.

    Parameters:
    - df (pd.DataFrame): The DataFrame to modify.

    Returns:
    - pd.DataFrame: The updated DataFrame with specified columns converted to 'category'.
    """
    for c in ["label", "subreddit", "year", "month", "day"]:
        matching = [col for col in df.columns if c in col]
        for col in matching:
            df[col] = df[col].astype("category")
    # remove 'deleted'
    df["text"] = df["text"].replace("deleted", "")

    return df


# Function to plot confusion matrix
def plot_confusion_matrix(cm, labels, title):
    """
    Plots a confusion matrix using seaborn's heatmap.

    Args:
        cm (numpy.ndarray): The confusion matrix to plot (2D array).
        labels (list of str): The list of class labels for the axes.
        title (str): The title for the plot.

    Returns:
        None: The function displays the confusion matrix as a heatmap.
    """
    plt.figure(figsize=(10, 7))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.show()


# Preprocessing function using Hugging Face tokenizer
def token_and_lemmatize_nb(text):
    # Initialize tools
    tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
    stop_words = set(STOP_WORDS)  # Use spaCy's stopwords
    lemmatizer = WordNetLemmatizer()

    # Tokenize text using Hugging Face tokenizer
    output = tokenizer.encode(text.lower())
    tokens = output.tokens  # Get tokenized words

    # Remove stopwords and lemmatize tokens
    processed_tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word.isalpha() and word not in stop_words
    ]

    # Rejoin tokens into a processed string
    return " ".join(processed_tokens)


# Function to predict sentiment using VADER
def vader_analysis(df):
    """
    Applies VADER sentiment analysis to a specified column in a DataFrame.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - text_column (str): The name of the column containing text to analyze.

    Returns:
    - pd.DataFrame: The DataFrame with two new columns:
        'vader_compound' for compound scores and
        'vader_sentiment' for sentiment classification ('positive', 'neutral', 'negative').
    """
    # Initialize the sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Apply VADER polarity scores and classification
    df["vader_compound"] = df["text"].apply(
        lambda x: analyzer.polarity_scores(x)["compound"]
    )
    df["vader_sentiment"] = df["vader_compound"].apply(
        lambda x: "positive" if x >= 0.05 else "negative" if x <= -0.05 else "neutral"
    )

    # Calculate accuracy and print classification report (assumes true labels are in a column named 'label')
    if "label" in df.columns:
        y_true = df["label"]
        y_pred = df["vader_sentiment"]

        # Calculate and print accuracy
        accuracy = accuracy_score(y_true, y_pred)
        print(f"Test set accuracy: {accuracy:.2f}")

        # Print classification report
        print("Classification Report:")
        print(classification_report(y_true, y_pred, zero_division=0))
    return df


# Preprocessing function
def token_and_lemmatize_rob(text):
    # Initialize tools
    stop_words = set(STOP_WORDS)
    lemmatizer = WordNetLemmatizer()

    tokens = text.split()  # Simple tokenization for Tfidf compatibility
    processed_tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word.isalpha() and word not in stop_words
    ]
    return " ".join(processed_tokens)


def tokenize_function(examples):
    # Tokenize using Hugging Face tokenizer
    tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    return tokenizer(examples["text"], padding="max_length", truncation=True)


# Load the saved model and tokenizer
# Tokenize and predict function
def predict_with_roberta(text):
    # Tokenize the input text
    save_path = "."
    roBERTa_model = RobertaForSequenceClassification.from_pretrained(save_path)
    tokenizer = RobertaTokenizer.from_pretrained(save_path)

    roBERTa_model.eval()

    inputs = tokenizer(
        text, padding=True, truncation=True, max_length=512, return_tensors="pt"
    )

    # Pass through the model
    with torch.no_grad():
        outputs = roBERTa_model(**inputs)
        logits = outputs.logits
        predicted_label = torch.argmax(logits, axis=1).item()  # Get predicted label
    return predicted_label
