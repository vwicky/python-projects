import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Example data: List of document pairs and their similarity scores
document_pairs = [
    ((1, 2), 0.8),
    ((1, 3), 0.6),
    ((2, 3), 0.9),
    # Add more document pairs and similarity scores as needed
]

class GraphPlotter:
    @staticmethod
    def show_3d_grap_of_similarity(document_pairs: list[tuple]) -> None:
        # Extracting data for plotting
        documents, similarities = zip(*[(pair, similarity) for pair, similarity in document_pairs])
        doc1, doc2 = zip(*documents)
        
        
        indices = documents
        x = [indicx[0] for indicx in indices]
        y = [indicx[1] for indicx in indices]
        z = similarities

        # Creating a 3D scatter plot
        fig = plt.figure("Similarity 3d Graph")
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, c='r', marker='o')

        # Adding labels
        ax.set_xlabel('Index of Document Pair')
        ax.set_ylabel('Index of Document Pair (Shifted)')
        ax.set_zlabel('Similarity Score')
        # Display the plot
        plt.show()
