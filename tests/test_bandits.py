from __future__ import absolute_import
from applab.bandit import BayesianBandit
import unittest
import random
from collections import Counter


class BanditTestCase(unittest.TestCase):

    def setUp(self):
        arms = [dict(id="black", trials=0, successes=0),
                dict(id="white", trials=0, successes=0)]
        self.bandit = BayesianBandit(arms)

    def choose_reward(self, arm_id):
        if random.random() > self.arm_probabilities[arm_id]:
            return 0.0
        return 1.0

    def simulate_experiment(self, n_sims=100):
        arm_ids = []
        for i in range(1, n_sims):
            arm_id = self.bandit.choose_arm()
            reward = self.choose_reward(arm_id)
            self.bandit.reward_arm(arm_id, reward)
            arm_ids.append(arm_id)
        return arm_ids

    def test_two_arms_high_difference(self):
        self.arm_probabilities = dict(black=0.8, white=0.2)
        arm_ids = self.simulate_experiment()
        counter = Counter(arm_ids)
        self.assertEqual(counter.most_common()[0][0], 'black')

    def test_two_arms_small_difference(self):
        self.arm_probabilities = dict(black=0.45, white=0.55)
        arm_ids = self.simulate_experiment(2000)
        counter = Counter(arm_ids)
        self.assertEqual(counter.most_common()[0][0], 'white')
