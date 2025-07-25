#!/usr/bin/env python3
"""
Test script for the modular LLM provider system.
"""

import sys
import os

# Add the autopr package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))


def test_imports() -> bool:
    """Test that all imports work correctly."""
    print("Testing imports...")

    try:
        # Test main package import
        from autopr.actions.llm import (
            get_llm_provider_manager,
            complete_chat,
            LLMProviderManager,
            MessageRole,
            LLMResponse,
        )

        print("✅ Main package imports successful")

        # Test individual provider imports
        from autopr.actions.llm import (
            OpenAIProvider,
            AnthropicProvider,
            GroqProvider,
            MistralProvider,
            PerplexityProvider,
            TogetherAIProvider,
        )

        print("✅ Provider imports successful")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_manager_creation() -> bool:
    """Test that the manager can be created."""
    print("\nTesting manager creation...")

    try:
        from autopr.actions.llm import get_llm_provider_manager

        manager = get_llm_provider_manager()
        print(f"✅ Manager created successfully")

        # Test provider info
        info = manager.get_provider_info()
        print(f"✅ Available providers: {info['available_providers']}")
        print(f"✅ Default provider: {info['default_provider']}")

        return True
    except Exception as e:
        print(f"❌ Manager creation failed: {e}")
        return False


def test_provider_availability() -> bool:
    """Test provider availability without API keys."""
    print("\nTesting provider availability...")

    try:
        from autopr.actions.llm import get_llm_provider_manager

        manager = get_llm_provider_manager()

        for provider_name in ["openai", "anthropic", "groq", "mistral", "perplexity", "together"]:
            provider = manager.get_provider(provider_name)
            if provider:
                print(f"✅ {provider_name} provider available")
            else:
                print(f"⚠️  {provider_name} provider not available (likely missing API key)")

        return True
    except Exception as e:
        print(f"❌ Provider availability test failed: {e}")
        return False


def test_backward_compatibility() -> bool:
    """Test that the old import still works."""
    print("\nTesting backward compatibility...")

    try:
        # This should work via the compatibility wrapper
        from autopr.actions.configurable_llm_provider import LLMProviderManager

        print("✅ Backward compatibility import successful")
        return True
    except ImportError as e:
        print(f"❌ Backward compatibility failed: {e}")
        return False


def main() -> int:
    """Run all tests."""
    print("🧪 Testing Modular LLM Provider System")
    print("=" * 50)

    tests = [
        test_imports,
        test_manager_creation,
        test_provider_availability,
        test_backward_compatibility,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Modular LLM system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
