import unittest
from pathlib import Path

from autopr.actions.platform_detection.config import PlatformConfig


class TestPlatformDetection(unittest.TestCase):
    def test_ai_platforms_loading(self):
        """Test that AI platforms are loaded correctly with valid structure."""
        # Get AI platforms
        ai_platforms = PlatformConfig.get_ai_platforms()

        # Verify we have at least one platform loaded
        self.assertGreaterEqual(len(ai_platforms), 1, "No AI platforms loaded")

        # Verify each platform has the required structure
        for platform_id, platform in ai_platforms.items():
            # Check required top-level fields
            self.assertEqual(
                platform_id, platform.get("id"), f"Platform ID mismatch for {platform_id}"
            )
            self.assertIsInstance(
                platform.get("name"), str, f"Platform {platform_id} missing or invalid 'name'"
            )
            self.assertIsInstance(
                platform.get("description"),
                str,
                f"Platform {platform_id} missing or invalid 'description'",
            )
            self.assertEqual(
                platform.get("category"),
                "ai_development",
                f"Platform {platform_id} has incorrect category",
            )

            # Verify detection section exists
            self.assertIn(
                "detection", platform, f"Platform {platform_id} missing 'detection' section"
            )

            # Log the platforms we're testing for visibility in test output
            print(f"✓ Verified platform: {platform['name']} ({platform_id})")

        # Log total number of platforms tested
        print(f"\n✅ Verified {len(ai_platforms)} AI platform configurations")

        # Verify platform structure for a sample platform
        if "cursor" in ai_platforms:
            cursor = ai_platforms["cursor"]
            self.assertEqual(cursor["name"], "Cursor")
            self.assertIn("detection", cursor)
            self.assertIn("project_config", cursor)
            self.assertIn("metadata", cursor)

    def test_platform_structure(self):
        """Test the structure of all loaded platforms."""
        all_platforms = PlatformConfig.get_all_platforms()
        self.assertGreater(len(all_platforms), 0, "No platforms were loaded")

        for platform_id, platform in all_platforms.items():
            print(f"\nTesting platform: {platform_id}")
            print(f"Platform data: {platform}")

            # Check required top-level fields
            self.assertEqual(
                platform_id, platform.get("id"), f"Platform ID mismatch for {platform_id}"
            )

            # Check detection section
            self.assertIn(
                "platform_detection",
                platform,
                f"Platform {platform_id} missing 'platform_detection' section",
            )
            detection = platform["platform_detection"]
            print(f"- Detection section: {detection}")

            # Check required detection fields
            for field in ["name", "category", "description"]:
                self.assertIn(
                    field, detection, f"Platform {platform_id} detection missing '{field}' field"
                )
                print(f"  - {field}: {detection[field]}")

            # The name and description should come from the detection section
            name = detection.get("name")
            self.assertIsInstance(
                name, str, f"Platform {platform_id} missing or invalid 'name' in detection section"
            )
            print(f"- Name from detection: {name}")

            description = detection.get("description")
            self.assertIsInstance(
                description,
                str,
                f"Platform {platform_id} missing or invalid 'description' in detection section",
            )
            print(f"- Description from detection: {description}")

            # Check optional list fields in detection
            for field in [
                "files",
                "dependencies",
                "folder_patterns",
                "commit_patterns",
                "content_patterns",
                "package_scripts",
            ]:
                if field in detection:
                    self.assertIsInstance(
                        detection[field],
                        list,
                        f"{field} should be a list in platform {platform_id}",
                    )

            # Check confidence_weights if present
            if "confidence_weights" in detection:
                self.assertIsInstance(
                    detection["confidence_weights"],
                    dict,
                    f"confidence_weights should be a dict in platform {platform_id}",
                )

            # Check project_configuration section
            self.assertIn(
                "project_configuration",
                platform,
                f"Platform {platform_id} missing 'project_configuration' section",
            )
            project_config = platform["project_configuration"]

            # Check required project_configuration fields
            self.assertIn(
                "name", project_config, f"Project config for {platform_id} missing 'name' field"
            )
            self.assertIn(
                "display_name",
                project_config,
                f"Project config for {platform_id} missing 'display_name' field",
            )
            self.assertIn(
                "description",
                project_config,
                f"Project config for {platform_id} missing 'description' field",
            )

            # Check optional list fields in project_configuration
            for field in ["common_files", "deployment_targets"]:
                if field in project_config:
                    self.assertIsInstance(
                        project_config[field],
                        list,
                        f"{field} should be a list in project config for {platform_id}",
                    )


if __name__ == "__main__":
    unittest.main()
