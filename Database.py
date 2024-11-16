# future implementation

from neo4j import GraphDatabase

# Neo4j connection setup
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def execute_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return result

# Initialize Neo4j connection
neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")


def add_word_node(neo4j_conn, word, embedding):
    query = """
    MERGE (w:Word {name: $word})
    SET w.embedding = $embedding
    """
    neo4j_conn.execute_query(query, {"word": word, "embedding": embedding})

def add_similarity_relationship(neo4j_conn, word1, word2, similarity_score, threshold=0.8):
    if similarity_score >= threshold:
        query = """
        MATCH (w1:Word {name: $word1}), (w2:Word {name: $word2})
        MERGE (w1)-[:SIMILAR {score: $similarity_score}]->(w2)
        """
        neo4j_conn.execute_query(query, {"word1": word1, "word2": word2, "similarity_score": similarity_score})


# Sample words and similarity data
words = ["food", "dinner", "meal", "water"]
embeddings = {
    "food": [0.2, 0.8, 0.5],
    "dinner": [0.2, 0.7, 0.6],
    "meal": [0.25, 0.75, 0.55],
    "water": [0.3, 0.6, 0.7]
}

similarity_scores = {
    ("food", "dinner"): 0.85,
    ("food", "meal"): 0.9,
    ("meal", "dinner"): 0.88,
    ("food", "water"): 0.4,  # Below threshold, so no relationship
}

# Adding words and relationships
for word, embedding in embeddings.items():
    add_word_node(neo4j_conn, word, embedding)

for (word1, word2), score in similarity_scores.items():
    add_similarity_relationship(neo4j_conn, word1, word2, score, threshold=0.8)


def get_similar_words(neo4j_conn, word):
    query = """
    MATCH (w:Word {name: $word})-[:SIMILAR]->(related)
    RETURN related.name AS similar_word
    """
    result = neo4j_conn.execute_query(query, {"word": word})
    return [record["similar_word"] for record in result]

# Example usage
similar_words = get_similar_words(neo4j_conn, "food")
print(f"Words similar to 'food': {similar_words}")


neo4j_conn.close()
