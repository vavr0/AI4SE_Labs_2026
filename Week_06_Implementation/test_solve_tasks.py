"""Generator tests use synthetic source files and a mocked API, never real keys."""

import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

from solve_tasks import Implementation, create_client, replace_body, solve_task


SOURCE = '''class Example:
    @property
    def value(self) -> int:
        pass

    def untouched(self):
        return 7
'''


class SolveTasksTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'sample.py'
        self.source.write_text(SOURCE, encoding='utf-8')
        self.target = {'file': 'sample.py', 'class': 'Example', 'method': 'value'}
        self.chunks = [{'id': str(i), 'file': 'sample.py', 'start_line': 1, 'end_line': 8, 'text': SOURCE} for i in range(5)]
        self.vectors = np.tile(np.array([[1, 0]], dtype=np.float32), (5, 1))
        self.client = Mock()
        self.client.responses.parse.return_value = SimpleNamespace(
            status='completed', output_parsed=Implementation(body='return 42'), usage=None,
        )

    def solve(self, client=None, replace_existing=False):
        with patch('solve_tasks.encode_texts', return_value=np.array([[1, 0]], dtype=np.float32)):
            return solve_task('Implement the requested value property.', self.target, self.root, self.chunks, self.vectors, object(), client, replace_existing=replace_existing)

    def test_patch_preserves_signature_decorator_and_other_method(self):
        result = replace_body(SOURCE, 'Example', 'value', 'return 42')
        self.assertIn('@property\n    def value(self) -> int:', result)
        self.assertIn('def untouched(self):\n        return 7', result)
        self.assertEqual(ast.parse(result).body[0].body[0].body[0].value.value, 42)

    def test_normalizes_a_first_line_without_the_remaining_method_margin(self):
        body = 'if False:\n            return 0\n        return 42'
        updated = replace_body(SOURCE, 'Example', 'value', body)
        namespace = {}
        exec(updated, namespace)
        self.assertEqual(namespace['Example']().value, 42)

    def test_rejects_unsafe_or_invalid_bodies(self):
        for body in ('pass', 'import os', 'return open("secret")', 'return (', 'def other():\n    return 1'):
            with self.subTest(body=body):
                with self.assertRaises((ValueError, SyntaxError)):
                    replace_body(SOURCE, 'Example', 'value', body)

    def test_dry_run_does_not_call_api_or_write_code(self):
        result = self.solve()
        self.assertEqual(result['status'], 'prepared')
        self.assertFalse(result['api_attempted'])
        self.assertEqual(len(result['retrieved']), 5)
        self.assertEqual(self.source.read_text(), SOURCE)

    def test_api_receives_exactly_five_chunks_and_response_is_written(self):
        result = self.solve(self.client)
        self.assertEqual(result['status'], 'updated')
        self.assertTrue(result['api_attempted'])
        self.client.responses.parse.assert_called_once()
        request = self.client.responses.parse.call_args.kwargs
        self.assertEqual(request['model'], 'gpt-5.4-nano')
        self.assertEqual(request['input'].count('\nCHUNK '), 5)
        self.assertIn('return 42', self.source.read_text())

    def test_invalid_response_does_not_modify_file(self):
        self.client.responses.parse.return_value.output_parsed = Implementation(body='import os')
        result = self.solve(self.client)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['generated_body'], 'import os')
        self.assertEqual(self.source.read_text(), SOURCE)

    def test_implemented_target_is_not_sent_to_api_again(self):
        self.source.write_text(SOURCE.replace('pass', 'return 42'), encoding='utf-8')
        result = self.solve(self.client)
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['api_attempted'])
        self.client.responses.parse.assert_not_called()

    def test_explicit_replacement_is_limited_to_the_selected_method(self):
        self.source.write_text(SOURCE.replace('pass', 'return 17'), encoding='utf-8')
        result = self.solve(self.client, replace_existing=True)
        self.assertEqual(result['status'], 'updated')
        self.client.responses.parse.assert_called_once()
        self.assertIn('return 42', self.source.read_text())
        self.assertIn('def untouched(self):\n        return 7', self.source.read_text())

    def test_path_traversal_is_rejected_before_api(self):
        self.target['file'] = '../outside.py'
        result = self.solve(self.client)
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['api_attempted'])
        self.client.responses.parse.assert_not_called()

    def test_client_uses_explicit_local_key_and_disables_retries(self):
        env_file = self.root / '.env'
        env_file.write_text('OPENAI_API_KEY=synthetic-test-key\n', encoding='utf-8')
        with patch('solve_tasks.OpenAI') as client_class:
            create_client(env_file)
        self.assertEqual(client_class.call_args.kwargs['api_key'], 'synthetic-test-key')
        self.assertEqual(client_class.call_args.kwargs['max_retries'], 0)
        self.assertEqual(client_class.call_args.kwargs['base_url'], 'https://api.openai.com/v1')


if __name__ == '__main__':
    unittest.main()
