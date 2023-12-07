from logic.algorithms import AlgorithmType
from logic.algorithms.Algorithm import Algorithm
from logic.algorithms.implementations import STabuSearch, GreedyAlgorithm, AdaptiveMemoryTabuSearch
from logic.algorithms.implementations.GoogleAlgorithm import GoogleAlgorithm, GoogleAlgoType


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
            case AlgorithmType.GOOGLE_GUIDED_LOCAL_SEARCH:
                return GoogleAlgorithm(GoogleAlgoType.GUIDED_LOCAL_SEARCH)
            case AlgorithmType.GOOGLE_SIMULATED_ANNEALING:
                return GoogleAlgorithm(GoogleAlgoType.SIMULATED_ANNEALING)
            case _:
                raise ValueError("Invalid Type")