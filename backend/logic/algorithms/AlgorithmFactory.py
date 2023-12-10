from logic.algorithms import AlgorithmType
from logic.algorithms.Algorithm import Algorithm
from logic.algorithms.implementations import STabuSearch, GreedyAlgorithm, AdaptiveMemoryTabuSearch
from logic.algorithms.implementations.GoogleAlgorithm import GoogleAlgorithm, GoogleAlgoType


class AlgorithmFactory:
    @staticmethod
    def create(algorithm_type:AlgorithmType,seconds_terminate:int) -> Algorithm:
        match algorithm_type:
            case AlgorithmType.GREEDY:
                return GreedyAlgorithm()
            case AlgorithmType.TABU:
                return STabuSearch()
            # case AlgorithmType.AM_TABU:
            #     return AdaptiveMemoryTabuSearch()
            case AlgorithmType.GOOGLE_GLS:
                return GoogleAlgorithm(GoogleAlgoType.GUIDED_LOCAL_SEARCH, seconds_terminate)
            case AlgorithmType.GOOGLE_SA:
                return GoogleAlgorithm(GoogleAlgoType.SIMULATED_ANNEALING, seconds_terminate)
            case AlgorithmType.GOOGLE_CW:
                return GoogleAlgorithm(GoogleAlgoType.CW_ONLY, seconds_terminate)
            case AlgorithmType.GOOGLE_TABU:
                return GoogleAlgorithm(GoogleAlgoType.GOOGLE_TABU, seconds_terminate)
            case _:
                raise ValueError("Invalid Type")