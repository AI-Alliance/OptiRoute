from logic.algorithms import AlgorithmType
from logic.algorithms.Algorithm import Algorithm
from logic.algorithms.implementations import STabuSearch, GreedyAlgorithm, AdaptiveMemoryTabuSearch
from logic.algorithms.implementations.GoogleAlgorithm import GoogleAlgorithm


class AlgorithmFactory:
    @staticmethod
    def create(algorithm_type:AlgorithmType) -> Algorithm:
        match algorithm_type:
            case AlgorithmType.GREEDY:
                return GreedyAlgorithm()
            case AlgorithmType.TABU:
                return STabuSearch()
            case AlgorithmType.AM_TABU:
                return AdaptiveMemoryTabuSearch()
            case AlgorithmType.GOOGLE:
                return GoogleAlgorithm()
            case _:
                raise ValueError("Invalid Type")