from random import betavariate


class BayesianBandit:
    def __init__(self, arms):
        self.arms = arms

    def choose_arm(self):
        probs = []
        for arm in self.arms:
            trials = arm['trials']
            successes = arm['successes']
            prob = betavariate(1 + successes, 1 + trials - successes)
            probs.append(prob)
        return self.arms[probs.index(max(probs))]['id']

    def reward_arm(self, arm_id, reward):
        arm = filter(lambda x: x['id'] == arm_id, self.arms)[0]
        arm['trials'] += 1
        if reward == 1:
            arm['successes'] += 1
