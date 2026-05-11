#!/usr/bin/env python3
import json
import unittest
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

from requests import Response

from letsdebughelper import letsdebug


class TestLetsdebug(unittest.TestCase):

    def setUp(self) -> None:
        self.url = "https://letsdebug.net"
        self.domain = "jeffistotallyawesome.space"
        self.test_id = 359646
        self.post_data: Dict[str, str] = {"method": "http-01", "domain": self.domain}
        self.bad_post_data: Dict[str, str] = {"metho": "http=01", "domain": self.domain}
        self.test_id_url: str = f"{self.url}/{self.domain}/{self.test_id}"
        self.get_bad_result: str = "Invalid request parameters.\n"
        self.post_result_text: str = '{"Domain":"jeffistotallyawesome.space","ID":359640}\n'
        self.post_bad_result: str = "Please provide a valid domain name and validation method.\n"

        self.get_result_dict: Dict[str, Any] = dict(
            id=self.test_id,
            domain=self.domain,
            method="http-01",
            status="Complete",
            created_at="2020-11-16T20:39:19.970198Z",
            started_at="2020-11-16T20:39:19.973775Z",
            completed_at="2020-11-16T20:39:22.855617Z",
            result=dict(problems=[
                dict(
                    name="CloudflareCDN",
                    explanation=(f"The domain {self.domain} is being served through Cloudflare CDN. "
                                 "Any Let's Encrypt certificate installed on the origin server will only encrypt "
                                 "traffic between the server and Cloudflare. It is strongly recommended that the SSL "
                                 "option 'Full SSL (strict)' be enabled."),
                    detail=("https://support.cloudflare.com/hc/en-us/articles/"
                            "200170416-What-do-the-SSL-options-mean-"),
                    severity="Warning",
                ),
            ], ),
        )
        self.get_result_text: str = json.dumps(self.get_result_dict)

    def _mock_response(
        self,
        status: int = 200,
        text: Optional[str] = None,
        json_data: Optional[Any] = None,
    ) -> Mock:
        mock_resp = Mock(spec=Response)
        mock_resp.status_code = status
        mock_resp.text = text
        mock_resp.json = Mock(return_value=json_data)
        return mock_resp

    @patch("requests.get")
    def test_le_get_call(self, mock_get: Mock) -> None:
        mock_get.return_value = self._mock_response(text=self.get_result_text)
        result: Response = letsdebug.le_get_call(check_url=self.test_id_url)
        self.assertEqual(result.text, self.get_result_text)

    @patch("requests.get")
    def test_le_get_call_passes_timeout(self, mock_get: Mock) -> None:
        """Hardens against regression: HTTP calls must carry a timeout."""
        mock_get.return_value = self._mock_response(text=self.get_result_text)
        letsdebug.le_get_call(check_url=self.test_id_url)
        self.assertEqual(mock_get.call_args.kwargs.get("timeout"), letsdebug.HTTP_TIMEOUT_SECS)

    @patch("requests.post")
    def test_le_post_call(self, mock_post: Mock) -> None:
        mock_post.return_value = self._mock_response(text=self.post_result_text)
        result: Response = letsdebug.le_post_call(post_data=self.post_data)
        self.assertEqual(result.text, self.post_result_text)

    @patch("requests.post")
    def test_le_post_call_passes_timeout(self, mock_post: Mock) -> None:
        """Hardens against regression: HTTP calls must carry a timeout."""
        mock_post.return_value = self._mock_response(text=self.post_result_text)
        letsdebug.le_post_call(post_data=self.post_data)
        self.assertEqual(mock_post.call_args.kwargs.get("timeout"), letsdebug.HTTP_TIMEOUT_SECS)

    @patch("requests.get")
    def test_decode_result_success(self, mock_get: Mock) -> None:
        mock_get.return_value = self._mock_response(json_data=self.get_result_dict)
        result: Response = letsdebug.le_get_call(check_url=self.test_id_url)
        self.assertEqual(letsdebug.decode_result(result=result), self.get_result_dict)

    def test_decode_result_invalid_json_exits_nonzero(self) -> None:
        bad_resp = Mock(spec=Response)
        bad_resp.json = Mock(side_effect=ValueError("not json"))
        with self.assertRaises(SystemExit) as cm:
            letsdebug.decode_result(result=bad_resp)
        self.assertEqual(cm.exception.code, 1)

    def test_check_status_200_does_not_exit(self) -> None:
        ok_resp = self._mock_response(status=200, text=self.get_result_text)
        # Should return without raising; SystemExit would propagate.
        letsdebug.check_status(result=ok_resp, result_json={"ok": True})

    def test_check_status_non_200_exits_nonzero(self) -> None:
        bad_resp = self._mock_response(status=400, text=self.get_bad_result)
        with self.assertRaises(SystemExit) as cm:
            letsdebug.check_status(result=bad_resp, result_json={"error": "bad"})
        self.assertEqual(cm.exception.code, 1)

    @patch("letsdebughelper.letsdebug.sleep", lambda _s: None)
    @patch("letsdebughelper.letsdebug.le_get_call")
    def test_check_debug_test_status_completes(self, mock_get_call: Mock) -> None:
        mock_get_call.return_value = self._mock_response(json_data={"status": "Complete", "result": {"problems": []}})
        result = letsdebug.check_debug_test_status(self.test_id_url)
        self.assertEqual(result.get("status"), "Complete")

    @patch("letsdebughelper.letsdebug.sleep", lambda _s: None)
    @patch("letsdebughelper.letsdebug.le_get_call")
    def test_check_debug_test_status_caps_polling(self, mock_get_call: Mock) -> None:
        """If the API never reports Complete, we bail out instead of looping forever."""
        mock_get_call.return_value = self._mock_response(json_data={"status": "Pending"})
        with self.assertRaises(SystemExit) as cm:
            letsdebug.check_debug_test_status(self.test_id_url)
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(mock_get_call.call_count, letsdebug.MAX_POLL_ATTEMPTS)
