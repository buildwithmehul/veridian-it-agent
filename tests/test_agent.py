import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agent import answer, process_active_tickets, POLICIES, REQUESTS, TICKETS, AUDIT_LOG, AUDIT_PATH

class AssignmentScenariosTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        AUDIT_LOG[:] = []
        with open(AUDIT_PATH, 'w', encoding='utf-8') as file:
            json.dump([], file, indent=2)

    def test_dataset_counts(self):
        self.assertEqual(len(POLICIES), 11)
        self.assertEqual(len(REQUESTS), 15)
        self.assertEqual(len(TICKETS), 10)

    def test_all_prescribed_requests_once(self):
        results = {request['id']: answer(request['request']) for request in REQUESTS}
        self.assertEqual(set(results), {f'REQ-{number:02d}' for number in range(1, 16)})
        expected = {
            'REQ-01': ('laptop', 'escalate', ['KB-03', 'ASSET-01']),
            'REQ-02': ('guest_wifi', 'resolve', ['KB-07']),
            'REQ-03': ('password', 'escalate', ['KB-01']),
            'REQ-04': ('software', 'escalate', ['KB-04']),
            'REQ-05': ('vpn', 'resolve', ['KB-02']),
            'REQ-06': ('printer', 'resolve', ['KB-05']),
            'REQ-07': ('home_office', 'escalate', ['KB-10']),
            'REQ-08': ('security_incident', 'escalate', ['KB-09']),
            'REQ-09': ('mailbox', 'resolve', ['KB-06']),
            'REQ-10': ('admin_access', 'escalate', []),
            'REQ-11': ('vpn', 'escalate', ['KB-02']),
            'REQ-12': ('expense', 'follow_up', ['KB-08']),
            'REQ-13': ('laptop', 'follow_up', ['KB-03', 'ASSET-01']),
            'REQ-14': ('software', 'escalate', ['KB-04']),
            'REQ-15': ('unclear', 'follow_up', [])
        }
        for request_id, (intent, action, sources) in expected.items():
            self.assertEqual(results[request_id]['intent'], intent)
            self.assertEqual(results[request_id]['action'], action)
            self.assertEqual(results[request_id]['sources'], sources)
            self.assertTrue(results[request_id]['audit_id'])
        self.assertEqual(results['REQ-08']['risk'], 'critical')
        self.assertEqual(len(AUDIT_LOG), 15)

    def test_password_boundary_and_follow_up_content(self):
        exactly_five = answer('I failed my password 5 times')
        self.assertEqual(exactly_five['action'], 'resolve')
        self.assertIn('self-service portal', exactly_five['response'])
        expense = answer('I cannot log into the expense tool')
        self.assertEqual(len(expense['follow_up']), 2)
        vague = answer('It is not working')
        self.assertEqual(len(vague['follow_up']), 2)

    def test_supplied_active_tickets_use_agent_workflow(self):
        processed = {ticket['id']: ticket for ticket in process_active_tickets()}
        expected = {
            'TK-1043': ('escalate', ['KB-03', 'ASSET-01'], True),
            'TK-1044': ('escalate', ['KB-04'], True),
            'TK-1047': ('escalate', ['KB-10'], True),
            'TK-1048': ('escalate', ['KB-09'], True)
        }
        self.assertEqual(set(processed), set(expected))
        for ticket_id, (action, sources, escalated) in expected.items():
            self.assertEqual(processed[ticket_id]['action'], action)
            self.assertEqual(processed[ticket_id]['source_policy'], sources)
            self.assertEqual(processed[ticket_id]['escalated'], escalated)

    def test_created_ticket_has_required_fields(self):
        result = answer('My account is locked after 6 password attempts')
        from src.agent import create_ticket
        ticket = create_ticket('Test Employee', 'test@veridian-corp.example', 'My account is locked after 6 password attempts', result)
        for field in ('id', 'employee', 'issue', 'category', 'priority', 'status', 'source_policy', 'action_taken', 'escalated'):
            self.assertIn(field, ticket)
        with open(ROOT / 'data/tickets.json', encoding='utf-8') as file:
            persisted = json.load(file)
        persisted.remove(ticket)
        TICKETS.remove(ticket)
        with open(ROOT / 'data/tickets.json', 'w', encoding='utf-8') as file:
            json.dump(persisted, file, indent=2)


if __name__ == '__main__':
    unittest.main()
