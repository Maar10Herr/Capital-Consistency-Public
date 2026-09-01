import json
import tempfile
import unittest
from pathlib import Path

from capital_consistency import audit


class RunManifestTest(unittest.TestCase):
    def _manifest(self, project_dir):
        return audit.run_manifest(
            command=["demo", "run"],
            inputs=[project_dir / "input.txt"],
            outputs=[project_dir / "output.txt"],
            assumptions=["fixed input"],
            project_dir=project_dir,
            solver="exact test solver",
            solver_status="completed",
            arithmetic="exact",
            claim_status="test evidence",
            tolerances={"absolute": 0.0},
            random_seed=7,
        )

    def test_manifest_is_repeatable_and_excludes_runtime_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            project_dir = Path(directory)
            (project_dir / "input.txt").write_text("input\n", encoding="utf-8")
            (project_dir / "output.txt").write_text("output\n", encoding="utf-8")

            first = self._manifest(project_dir)
            second = self._manifest(project_dir)

            self.assertEqual(first, second)
            self.assertEqual(
                json.dumps(first, sort_keys=True),
                json.dumps(second, sort_keys=True),
            )
            self.assertEqual(first["manifest_schema"], "capital_consistency_run/v3")
            self.assertEqual(
                first["package_versions"]["capital-consistency"], audit.__version__
            )
            for volatile_key in ("timestamp_utc", "platform", "python", "git_commit"):
                self.assertNotIn(volatile_key, first)

    def test_manifest_rejects_symbolic_links(self):
        with tempfile.TemporaryDirectory() as directory:
            project_dir = Path(directory)
            (project_dir / "target.txt").write_text("target\n", encoding="utf-8")
            (project_dir / "output.txt").write_text("output\n", encoding="utf-8")
            link = project_dir / "input.txt"
            link.symlink_to(project_dir / "target.txt")
            with self.assertRaisesRegex(ValueError, "symbolic links"):
                audit.run_manifest(
                    command=["demo"],
                    inputs=[link],
                    outputs=[project_dir / "output.txt"],
                    assumptions=[],
                    project_dir=project_dir,
                    solver="test",
                    solver_status="completed",
                    arithmetic="exact",
                    claim_status="test",
                    tolerances={},
                )

    def test_manifest_rejects_external_alias_into_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project_dir = root / "project"
            project_dir.mkdir()
            (project_dir / "input.txt").write_text("input\n", encoding="utf-8")
            alias = root / "alias"
            alias.symlink_to(project_dir, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "outside project"):
                audit.run_manifest(
                    command=["demo"],
                    inputs=[alias / "input.txt"],
                    outputs=[],
                    assumptions=[],
                    project_dir=project_dir,
                    solver="test",
                    solver_status="completed",
                    arithmetic="exact",
                    claim_status="test",
                    tolerances={},
                )

    def test_manifest_rejects_duplicate_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            project_dir = Path(directory)
            (project_dir / "input.txt").write_text("input\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate input"):
                audit.run_manifest(
                    command=["demo"],
                    inputs=[project_dir / "input.txt", project_dir / "input.txt"],
                    outputs=[],
                    assumptions=[],
                    project_dir=project_dir,
                    solver="test",
                    solver_status="completed",
                    arithmetic="exact",
                    claim_status="test",
                    tolerances={},
                )


if __name__ == "__main__":
    unittest.main()
