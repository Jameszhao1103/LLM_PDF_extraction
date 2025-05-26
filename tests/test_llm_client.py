import unittest
from unittest.mock import patch, MagicMock
from src.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):

    @patch('src.llm_client.requests.post')
    def test_send_request_success(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'success'}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        llm_client = LLMClient()
        content = "Sample content"
        prompt = "What is this about?"

        # Act
        response = llm_client.send_request(content, prompt)

        # Assert
        self.assertEqual(response, {'result': 'success'})
        mock_post.assert_called_once()

    @patch('src.llm_client.requests.post')
    def test_send_request_failure(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        llm_client = LLMClient()
        content = "Sample content"
        prompt = "What is this about?"

        # Act
        response = llm_client.send_request(content, prompt)

        # Assert
        self.assertIsNone(response)
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()