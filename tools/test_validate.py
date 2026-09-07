"""Exercise repository validation against corrupted candidate contract inputs."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ("tools", "schemas", "decisions", "spec", "profiles", "compat", "conformance"):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(ROOT / "VERSION", self.root / "VERSION")

    def rewrite(self, name, change):
        path = self.root / name
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def assert_rejected(self, message):
        result = subprocess.run([sys.executable, str(self.root / "tools/validate.py")],
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stdout + result.stderr)

    def test_missing_rule_coverage(self):
        for path in (self.root / "conformance/profiles").glob("extent-*.json"):
            path.unlink()
        self.assert_rejected("uncovered rules: ['R01']")

    def test_wrong_profile_rule(self):
        self.rewrite("conformance/profiles/extent-exact.json",
                     lambda case: case.update(rules=["E01"]))
        self.assert_rejected("unknown profile rules")

    def test_duplicate_case_identity(self):
        shutil.copyfile(self.root / "conformance/profiles/extent-exact.json",
                        self.root / "conformance/profiles/duplicate.json")
        self.assert_rejected("duplicate case ID")

    def test_incorrect_schema_expectation(self):
        self.rewrite("conformance/contracts/manifest-profile-unknown.json",
                     lambda case: case.update(valid=True))
        self.assert_rejected("schema outcome differs")

    def test_undocumented_rule(self):
        self.rewrite("profiles/registry.json",
                     lambda registry: registry["profiles"][0]["rules"].append("R99"))
        self.assert_rejected("registry rules differ")


if __name__ == "__main__":
    unittest.main()
