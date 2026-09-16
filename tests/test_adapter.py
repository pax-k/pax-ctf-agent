import json
import os
import subprocess
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ctf_adapter import paths
from ctf_adapter.koth import (
    ApprovalError,
    apply_patch,
    prepare_flag_submission,
    prepare_patch,
    submit_flag,
)
from ctf_adapter.runner import ToolContractError, ToolRunner, ToolSpec
from ctf_adapter.scope import EngagementScope, ScopeError


class AdapterContractTest(unittest.TestCase):
    COMMON_RESULT_FIELDS = {
        "tool",
        "toolVersion",
        "category",
        "asset",
        "commandSummary",
        "startedAt",
        "durationMs",
        "exitCode",
        "timedOut",
        "stdoutPath",
        "stderrPath",
        "createdArtifacts",
        "artifactHashes",
        "validationState",
    }

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.input = self.root / "input"
        self.output = self.root / "output"
        self.input.mkdir()
        self.output.mkdir()
        paths.INPUT_ROOT = self.input
        paths.OUTPUT_ROOT = self.output
        self.scope = EngagementScope(
            engagement_id="test",
            categories=frozenset({"reverse", "osint"}),
            targets=("example.com", "fixture-user"),
            osint_sources=("media.example",),
            koth={},
        )

    def tearDown(self):
        self.temporary.cleanup()

    def assert_common_result(self, result):
        self.assertTrue(self.COMMON_RESULT_FIELDS.issubset(result))

    def test_input_path_rejects_parent_traversal(self):
        with self.assertRaises(paths.PathBoundaryError):
            paths.input_path("../outside")

    def test_input_path_rejects_escaping_symlink(self):
        outside = self.root / "outside"
        outside.write_text("outside", encoding="utf-8")
        (self.input / "link").symlink_to(outside)
        with self.assertRaises(paths.PathBoundaryError):
            paths.input_path("link")

    def test_input_directory_rejects_nested_escaping_symlink(self):
        directory = self.input / "tree"
        directory.mkdir()
        outside = self.root / "outside"
        outside.write_text("outside", encoding="utf-8")
        (directory / "link").symlink_to(outside)
        with self.assertRaises(paths.PathBoundaryError):
            paths.input_path("tree")

    def test_scope_rejects_unlisted_target(self):
        with self.assertRaises(ScopeError):
            self.scope.require_target("https://not-example.invalid")

    def test_scope_distinguishes_subject_and_source(self):
        self.assertEqual(self.scope.require_subject("fixture-user"), "fixture-user")
        self.assertEqual(self.scope.require_target("https://media.example/a", osint=True), "https://media.example/a")

    def test_scope_rejects_expired_time_window(self):
        now = datetime.now(timezone.utc)
        expired = EngagementScope(
            engagement_id="expired",
            categories=frozenset({"reverse"}),
            targets=("example.com",),
            osint_sources=(),
            koth={},
            starts_at=now - timedelta(hours=2),
            ends_at=now - timedelta(hours=1),
        )
        with self.assertRaises(ScopeError):
            expired.require_category("reverse")

    def test_runner_uses_argument_array_and_writes_result(self):
        asset = self.input / "artifact.txt"
        asset.write_text("$(touch should-not-exist)", encoding="utf-8")
        spec = ToolSpec(
            name="fixture_echo",
            category="shared",
            binary="/bin/echo",
            version="test",
            kind="artifact",
            args=("{asset}",),
            timeout=5,
            options={},
        )
        result = ToolRunner(self.scope, "reverse").run(spec, asset="artifact.txt")
        self.assert_common_result(result)
        self.assertEqual(result["validationState"], "completed")
        self.assertFalse((self.root / "should-not-exist").exists())
        result_files = list((self.output / "evidence").glob("*/result.json"))
        self.assertEqual(len(result_files), 1)

    def test_unknown_option_is_rejected(self):
        asset = self.input / "artifact.txt"
        asset.write_text("fixture", encoding="utf-8")
        spec = ToolSpec("fixture", "shared", "/bin/echo", "test", "artifact", ("{asset}",), 5, {})
        with self.assertRaises(ToolContractError):
            ToolRunner(self.scope, "reverse").run(spec, asset="artifact.txt", options={"args": "--help"})

    def test_koth_patch_requires_the_exact_prepared_digest(self):
        checkout = self.output / "koth-checkout"
        checkout.mkdir()
        (checkout / "service.txt").write_text("old\n", encoding="utf-8")
        subprocess.run(["git", "init", "--quiet", str(checkout)], check=True)
        subprocess.run(["git", "-C", str(checkout), "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", str(checkout), "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(checkout), "add", "service.txt"], check=True)
        subprocess.run(["git", "-C", str(checkout), "commit", "--quiet", "-m", "fixture"], check=True)

        patch_asset = self.input / "fix.patch"
        patch_asset.write_text(
            "diff --git a/service.txt b/service.txt\n"
            "--- a/service.txt\n"
            "+++ b/service.txt\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n",
            encoding="utf-8",
        )
        scope = EngagementScope(
            engagement_id="test",
            categories=frozenset({"koth"}),
            targets=("127.0.0.1",),
            osint_sources=(),
            koth={"allowPatchApplication": True},
        )

        prepared = prepare_patch(scope, "fix.patch", "koth-checkout")
        self.assert_common_result(prepared)
        prepared_details = prepared["details"]
        with self.assertRaises(ApprovalError):
            apply_patch(scope, prepared_details["bundle"].removeprefix("output/"), "wrong-digest")
        self.assertEqual((checkout / "service.txt").read_text(encoding="utf-8"), "old\n")

        applied = apply_patch(
            scope,
            prepared_details["bundle"].removeprefix("output/"),
            prepared_details["approvalDigest"],
        )
        self.assert_common_result(applied)
        self.assertEqual(applied["validationState"], "completed")
        self.assertEqual((checkout / "service.txt").read_text(encoding="utf-8"), "new\n")
        self.assertTrue((self.output / applied["details"]["rollback"].removeprefix("output/")).is_file())
        subprocess.run(["git", "-C", str(checkout), "apply", "--reverse", str(patch_asset)], check=True)
        with self.assertRaises(ApprovalError):
            apply_patch(
                scope,
                prepared_details["bundle"].removeprefix("output/"),
                prepared_details["approvalDigest"],
            )

    def test_koth_flag_requires_a_separate_exact_digest(self):
        received: list[dict[str, str]] = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802 - stdlib callback name
                size = int(self.headers["Content-Length"])
                received.append(json.loads(self.rfile.read(size)))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"accepted":true}')

            def log_message(self, _format, *_args):
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        endpoint = f"http://127.0.0.1:{server.server_port}/submit"
        scope = EngagementScope(
            engagement_id="test",
            categories=frozenset({"koth"}),
            targets=("127.0.0.1",),
            osint_sources=(),
            koth={"allowFlagSubmission": True, "submissionEndpoints": [endpoint]},
        )
        try:
            prepared = prepare_flag_submission(
                scope,
                flag="OMNI{synthetic}",
                target="fixture-service",
                team="fixture-team",
                endpoint=endpoint,
            )
            self.assert_common_result(prepared)
            prepared_details = prepared["details"]
            with self.assertRaises(ApprovalError):
                submit_flag(scope, prepared_details["bundle"].removeprefix("output/"), "wrong-digest")
            self.assertEqual(received, [])

            submitted = submit_flag(
                scope,
                prepared_details["bundle"].removeprefix("output/"),
                prepared_details["approvalDigest"],
            )
            self.assert_common_result(submitted)
            self.assertEqual(submitted["validationState"], "completed")
            self.assertEqual(received, [{"flag": "OMNI{synthetic}", "target": "fixture-service", "team": "fixture-team"}])
            with self.assertRaises(ApprovalError):
                submit_flag(
                    scope,
                    prepared_details["bundle"].removeprefix("output/"),
                    prepared_details["approvalDigest"],
                )
            self.assertEqual(len(received), 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
