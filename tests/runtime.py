import unittest
import requests
import json
from pipelines.transformer import TransformedTournamentData
from shared.lprint import lprint
from shared.const import API_BASE

class TestTransformerRuntime(unittest.TestCase):
    transformed: TransformedTournamentData

    def setUp(self, transformed: TransformedTournamentData):
        self.transformed = transformed

    def test_entry_count(self):
        input_count = len(self.mock_input['entries'])
        output_count = len(self.transformed_data.team_results)
        self.assertEqual(input_count, output_count, "Number of input entries should match number of output entries in team_results")

    def test_round_count(self):
        input_prelim_count = sum(1 for r in self.mock_input['rounds'] if r['type'] == 'prelim')
        input_elim_count = sum(1 for r in self.mock_input['rounds'] if r['type'] == 'elim')

        output_prelim_wins = sum(team['prelim_wins'] for team in self.transformed_data.team_results)
        output_prelim_losses = sum(team['prelim_losses'] for team in self.transformed_data.team_results)
        output_elim_wins = sum(team['elim_wins'] for team in self.transformed_data.team_results)
        output_elim_losses = sum(team['elim_losses'] for team in self.transformed_data.team_results)

        self.assertEqual(input_prelim_count, output_prelim_wins + output_prelim_losses, "Sum of prelim wins and losses should match number of prelim rounds")
        self.assertEqual(input_elim_count, output_elim_wins + output_elim_losses, "Sum of elim wins and losses should match number of elim rounds")

    def test_judge_count(self):
        input_judge_count = len(self.mock_input['judges'])
        output_judge_count = len(self.transformed_data.judge_results)
        self.assertEqual(input_judge_count, output_judge_count, "Number of input judges should match number of output judges")

    def test_unique_judge_names(self):
        input_judge_names = set(judge['name'] for judge in self.mock_input['judges'])
        output_judge_ids = set(judge['judge_id'] for judge in self.transformed_data.judge_results)
        self.assertEqual(input_judge_names, output_judge_ids, "Unique judge names in input should match judge_results.judge_id")

    def test_judge_prelim_count(self):
        for judge in self.transformed_data.judge_results:
            output_prelim_count = judge['num_prelims']
            output_team_prelim_ballots = sum(
                team['prelim_ballots_won'] + team['prelim_ballots_lost'] for team in self.transformed_data.team_results
            )
            self.assertEqual(output_prelim_count, output_team_prelim_ballots, "Number of prelim rounds judged should match the total of prelim ballots won and lost by teams")

    def test_judge_elim_count(self):
        for judge in self.transformed_data.judge_results:
            output_elim_count = judge['num_elims']
            output_team_elim_ballots = sum(
                team['elim_ballots_won'] + team['elim_ballots_lost'] for team in self.transformed_data.team_results
            )
            self.assertEqual(output_elim_count, output_team_elim_ballots, "Number of elim rounds judged should match the total of elim ballots won and lost by teams")

    def test_unique_school_count(self):
        input_school_count = len(set(entry['school'] for entry in self.mock_input['entries']))
        output_school_count = len(set(team['school'] for team in self.transformed_data.team_results))
        self.assertEqual(input_school_count, output_school_count, "Number of unique schools in input should match the number of unique schools in output")

    def test_rounds_match(self):
        input_rounds = sum(len(entry['rounds']) for entry in self.mock_input['entries'])
        output_rounds = sum(len(team['rounds']) for team in self.transformed_data.team_results)
        self.assertEqual(input_rounds, output_rounds, "Number of rounds in input should match the number of rounds in output")

    def test_no_login_to_tabroom(self):
        for entry in self.mock_input['entries']:
            self.assertNotIn('Login to Tabroom', entry['name'], "Entry name should not contain 'Login to Tabroom'")

def process_runtime_tests(job_id: str | None, transformed_data: TransformedTournamentData):
    unittest.main()
    lprint(job_id, "Testing", None, str(unittest.result))

