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

    # 2. Convert the string representation of the 'contexts' list back into an actual list
    # When pandas saves a list to CSV, it becomes a string like '["doc1", "doc2"]'.
    # We need to convert it back to a list object for Ragas.
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



# ### How to Use It

# 1.  **Prerequisite:** Make sure you have successfully run the `process_for_ragas.py` script and have the `ragas_input_data.csv` file in your directory.
# 2.  **Save the Code:** Save the script above as `evaluate_with_ragas.py`.
# 3.  **Run from Terminal:** Open your terminal in the same project directory and run the script:
#     bash
#     python evaluate_with_ragas.py