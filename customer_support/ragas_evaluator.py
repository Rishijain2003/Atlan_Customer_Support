import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
import logging
import ast # Used to safely evaluate string-formatted lists
import os 
# --- Configuration ---
INPUT_FILE = "ragas_input_data.csv"

# --- Main Script ---
from dotenv import load_dotenv
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key =  os.getenv("Openai_api_key")
if not api_key:
    raise ValueError("OPENAI_API_KEY is missing. Please check your .env file.")
if __name__ == "__main__":
    # 1. Load the data prepared by the previous script
    try:
        df = pd.read_csv(INPUT_FILE)
        logger.info(f"Successfully loaded data from '{INPUT_FILE}'.")
    except FileNotFoundError:
        logger.error(f"Error: The input file '{INPUT_FILE}' was not found. Please run 'process_for_ragas.py' first.")
        exit()


    try:
        df['contexts'] = df['contexts'].apply(ast.literal_eval)
    except Exception as e:
        logger.error(f"Error converting 'contexts' column from string to list: {e}")
        logger.error("Please ensure the 'contexts' column in your CSV is a valid string representation of a Python list.")
        exit()


    # 3. Convert the pandas DataFrame to a Hugging Face Dataset
    dataset = Dataset.from_pandas(df)
    logger.info("Converted DataFrame to Hugging Face Dataset.")

    # 4. Define the metrics for evaluation
    metrics_to_use = [
        faithfulness,
        answer_relevancy,
        context_precision,
    ]

    # 5. Run the evaluation
    logger.info("🔬 Running Ragas evaluation... This may take a few minutes.")
    result = evaluate(
        dataset=dataset,
        metrics=metrics_to_use,
    )

    # 6. Display the results
    df_results = result.to_pandas()
    logger.info("✅ Evaluation complete!")

    print("\n--- Ragas Evaluation Results ---")
    print(df_results)

    print("\n--- Average Scores ---")
    print(df_results.mean(numeric_only=True))
    print("------------------------")



