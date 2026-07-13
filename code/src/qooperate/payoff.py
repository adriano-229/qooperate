from dataclasses import dataclass

from qooperate.agent import COOPERATE, DEFECT


@dataclass(frozen=True)
class PayoffMatrix:
    T: float = 5.0
    R: float = 3.0
    P: float = 1.0
    S: float = 0.0

    def __post_init__(self):
        assert self.T > self.R > self.P > self.S
        assert 2 * self.R > self.T + self.S

    def payoff(self, my_action: int, other_action: int) -> float:
        table = {(COOPERATE, COOPERATE): self.R, (COOPERATE, DEFECT): self.S,
                 (DEFECT, COOPERATE): self.T, (DEFECT, DEFECT): self.P}
        return table[(my_action, other_action)]
