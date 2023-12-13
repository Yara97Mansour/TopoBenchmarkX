from abc import ABC, abstractmethod

import hydra
from omegaconf import DictConfig
from torch_geometric.data import Data

# logger = logging.getLogger(__name__)


class AbstractLoader(ABC):
    """Abstract class that provides an interface to load signals (audio)"""

    def __init__(self, cfg: DictConfig):
        self.cfg = cfg

    @abstractmethod
    def load(self, file: str, label) -> Data:
        """Load data into Data.

        Parameters:
          :file: Path to audio file to load
          :label: Label can be any type, lately passed as a value to the dict

        :return:
        """
