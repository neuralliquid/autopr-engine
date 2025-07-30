import unittest

from autopr.actions.platform_detection.config import PlatformConfigManager


class TestPlatformDetection(unittest.TestCase):
    def test_ai_platforms_loading(self):
        """Test that AI platforms are loaded correctly with valid structure."""
        # Get AI platforms
        ai_platforms = PlatformConfigManager().get_ai_platforms()

        # Verify we have at least one platform loaded
        assert len(ai_platforms) >= 1, "No AI platforms loaded"

        # Verify each platform has the required structure
        for platform_id, platform in ai_platforms.items():
            # Check required top-level fields
            assert platform_id == platform.get("id"), f"Platform ID mismatch for {platform_id}"
            assert isinstance(
                platform.get("name"), str
            ), f"Platform {platform_id} missing or invalid 'name'"
            assert isinstance(
                platform.get("description"), str
            ), f"Platform {platform_id} missing or invalid 'description'"
            assert (
                platform.get("category") == "ai_development"
            ), f"Platform {platform_id} has incorrect category"

            # Verify detection section exists
            assert "detection" in platform, f"Platform {platform_id} missing 'detection' section"

            # Log the platforms we're testing for visibility in test output

        # Log total number of platforms tested

        # Verify platform structure for a sample platform
        if "cursor" in ai_platforms:
            cursor = ai_platforms["cursor"]
            assert cursor["name"] == "Cursor"
            assert "detection" in cursor
            assert "project_config" in cursor
            assert "metadata" in cursor

    def test_platform_structure(self):
        """Test the structure of all loaded platforms."""
        all_platforms = PlatformConfigManager().get_all_platforms()
        assert len(all_platforms) > 0, "No platforms were loaded"

        for platform_id, platform in all_platforms.items():

            # Check required top-level fields
            assert platform_id == platform.get("id"), f"Platform ID mismatch for {platform_id}"

            # Check detection section
            assert (
                "platform_detection" in platform
            ), f"Platform {platform_id} missing 'platform_detection' section"
            detection = platform["platform_detection"]

            # Check required detection fields
            for field in ["name", "category", "description"]:
                assert (
                    field in detection
                ), f"Platform {platform_id} detection missing '{field}' field"

            # The name and description should come from the detection section
            name = detection.get("name")
            assert isinstance(
                name, str
            ), f"Platform {platform_id} missing or invalid 'name' in detection section"

            description = detection.get("description")
            assert isinstance(
                description, str
            ), f"Platform {platform_id} missing or invalid 'description' in detection section"

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
                    assert isinstance(
                        detection[field], list
                    ), f"{field} should be a list in platform {platform_id}"

            # Check confidence_weights if present
            if "confidence_weights" in detection:
                assert isinstance(
                    detection["confidence_weights"], dict
                ), f"confidence_weights should be a dict in platform {platform_id}"

            # Check project_configuration section
            assert (
                "project_configuration" in platform
            ), f"Platform {platform_id} missing 'project_configuration' section"
            project_config = platform["project_configuration"]

            # Check required project_configuration fields
            assert (
                "name" in project_config
            ), f"Project config for {platform_id} missing 'name' field"
            assert (
                "display_name" in project_config
            ), f"Project config for {platform_id} missing 'display_name' field"
            assert (
                "description" in project_config
            ), f"Project config for {platform_id} missing 'description' field"

            # Check optional list fields in project_configuration
            for field in ["common_files", "deployment_targets"]:
                if field in project_config:
                    assert isinstance(
                        project_config[field], list
                    ), f"{field} should be a list in project config for {platform_id}"


if __name__ == "__main__":
    unittest.main()
