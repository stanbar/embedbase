from typing import List, Union
import uvicorn
from embedbase import get_app
from embedbase.database.memory_db import MemoryDatabase
from embedbase.embedding.base import Embedder
from sentence_transformers import SentenceTransformer


# pylint: disable=missing-class-docstring
class LocalEmbedder(Embedder):
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, model: str = EMBEDDING_MODEL, **kwargs):
        super().__init__(**kwargs)
        self.model = SentenceTransformer(model)
        self._dimensions = self.model.get_sentence_embedding_dimension()

    @property
    def dimensions(self) -> int:
        """
        Return the dimensions of the embeddings
        :return: dimensions of the embeddings
        """
        return self._dimensions

    def is_too_big(self, text: str) -> bool:
        """
        Check if text is too big to be embedded,
        delegating the splitting UX to the caller
        :param text: text to check
        :return: True if text is too big, False otherwise
        """
        return len(text) > self.model.get_max_seq_length()

    async def embed(self, data: Union[List[str], str]) -> List[List[float]]:
        """
        Embed a list of texts
        :param texts: list of texts
        :return: list of embeddings
        """
        embeddings = self.model.encode(data)
        return embeddings.tolist() if isinstance(data, list) else [embeddings.tolist()]


app = get_app().use_db(MemoryDatabase()).use_embedder(LocalEmbedder()).run()


# pylint: disable=missing-function-docstring
def run_app():
    print(
        # pylint: disable=anomalous-backslash-in-string
        """
                 _           _   _         _               _          _         
        /\ \        /\_\/\_\ _    / /\            /\ \       /\ \       
       /  \ \      / / / / //\_\ / /  \          /  \ \     /  \ \____  
      / /\ \ \    /\ \/ \ \/ / // / /\ \        / /\ \ \   / /\ \_____\ 
     / / /\ \_\  /  \____\__/ // / /\ \ \      / / /\ \_\ / / /\/___  / 
    / /_/_ \/_/ / /\/________// / /\ \_\ \    / /_/_ \/_// / /   / / /  
   / /____/\   / / /\/_// / // / /\ \ \___\  / /____/\  / / /   / / /   
  / /\____\/  / / /    / / // / /  \ \ \__/ / /\____\/ / / /   / / /    
 / / /______ / / /    / / // / /____\_\ \  / / /______ \ \ \__/ / /     
/ / /_______\\/_/    / / // / /__________\/ / /_______\ \ \___\/ /      
\/__________/ _      \/_/ \/_____________/\/__________/  \/_____/       
             / /\            / /\               / /\         /\ \       
            / /  \          / /  \             / /  \       /  \ \      
           / / /\ \        / / /\ \           / / /\ \__   / /\ \ \     
          / / /\ \ \      / / /\ \ \         / / /\ \___\ / / /\ \_\    
         / / /\ \_\ \    / / /  \ \ \        \ \ \ \/___// /_/_ \/_/    
        / / /\ \ \___\  / / /___/ /\ \        \ \ \     / /____/\       
       / / /  \ \ \__/ / / /_____/ /\ \   _    \ \ \   / /\____\/       
      / / /____\_\ \  / /_________/\ \ \ /_/\__/ / /  / / /______       
     / / /__________\/ / /_       __\ \_\\ \/___/ /  / / /_______\      
     \/_____________/\_\___\     /____/_/ \_____\/   \/__________/      
                                                                                                
                 [-0.005, 0.012, -0.008, ..., -0.010]
        """
    )
    uvicorn.run("embedbase:app", host="0.0.0.0")


if __name__ == "__main__":
    run_app()
