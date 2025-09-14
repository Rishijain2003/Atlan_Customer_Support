import pandas as pd
import logging
from rag_builder import RAGAgent 


PINECONE_INDEX_NAME = "atlandb"


INPUT_CSV_FILE = "evaluation_set.csv"
OUTPUT_CSV_FILE = "ragas_input_data.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_evaluation_set(agent, input_df):
    """
    Runs each question from the input DataFrame through the RAG agent
    and collects the answers and contexts.
    """
    answers = []
    contexts_list = []

    total_questions = len(input_df)
    logger.info(f"Starting processing for {total_questions} questions...")

    for index, row in input_df.iterrows():
        question = row['question']
        logger.info(f"Processing question {index + 1}/{total_questions}: '{question}'")

        try:
       
            result_state = agent.invoke({"question": question})

            answer_text = result_state['answer'].answer
            answers.append(answer_text)


            retrieved_docs = result_state['context']
            context_strings = [doc.page_content for doc in retrieved_docs]
            contexts_list.append(context_strings)

        except Exception as e:
            logger.error(f"Failed to process question {index + 1}: {e}")
            answers.append("")
            contexts_list.append([])

    input_df['answer'] = answers
    input_df['contexts'] = contexts_list

    return input_df


if __name__ == "__main__":

    rag_pipeline = RAGAgent(index_name=PINECONE_INDEX_NAME)
    rag_agent = rag_pipeline.build()
    logger.info("RAG Agent and graph built successfully.")
    try:
        df_eval = pd.read_csv(INPUT_CSV_FILE, header=None, names=['question', 'ground_truth'])
        logger.info(f"Loaded {len(df_eval)} questions from '{INPUT_CSV_FILE}'.")
    except FileNotFoundError:
        logger.error(f"Error: The input file '{INPUT_CSV_FILE}' was not found.")
        exit()

    final_df = process_evaluation_set(rag_agent, df_eval)

    final_df.to_csv(OUTPUT_CSV_FILE, index=False)
    logger.info(f"Processing complete. Output saved to '{OUTPUT_CSV_FILE}'.")



