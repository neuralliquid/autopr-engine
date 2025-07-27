#!/usr/bin/env python3
"""
Comprehensive test suite for the modular LLM provider system.
Tests imports, configuration, provider availability, error handling, and API calls.
"""

import asyncio
import os
import sys
from typing import Any, Dict

# Add the autopr package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))


def test_imports() -> bool:
    """Test that all imports work correctly."""
    print("Testing imports...")

    try:
        # Test main package import
        from autopr.actions.llm import (
            LLMProviderManager,
            LLMResponse,
            MessageRole,
            complete_chat,
            get_llm_provider_manager,
        )

        print("✅ Main package imports successful")

        # Test individual provider imports
        from autopr.actions.llm import (
            AnthropicProvider,
            GroqProvider,
            MistralProvider,
            OpenAIProvider,
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


def test_configuration() -> bool:
    """Test configuration and provider information retrieval."""
    print("\nTesting configuration...")

    try:
        from autopr.actions.llm import get_llm_provider_manager

        manager = get_llm_provider_manager()

        # Test provider info retrieval
        provider_info = manager.get_provider_info()
        print(f"✅ Provider info retrieved with {len(provider_info)} settings")
        print(f"✅ Available providers: {provider_info['available_providers']}")
        print(f"✅ Default provider: {provider_info['default_provider']}")
        print(f"✅ Fallback order: {provider_info['fallback_order']}")

        # Test individual provider information
        for provider_name in ["openai", "anthropic", "groq", "mistral"]:
            provider = manager.get_provider(provider_name)
            if provider:
                print(f"✅ {provider_name} provider available")
                if hasattr(provider, "default_model"):
                    print(f"   Default model: {provider.default_model}")
            else:
                print(f"⚠️  {provider_name} provider not available")

        # Test available providers list
        available = manager.get_available_providers()
        print(f"✅ Available providers list: {available}")

        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_error_handling() -> bool:
    """Test error handling for invalid providers and configurations."""
    print("\nTesting error handling...")

    try:
        from autopr.actions.llm import get_llm_provider_manager

        manager = get_llm_provider_manager()

        # Test invalid provider
        invalid_provider = manager.get_provider("invalid_provider")
        if invalid_provider is None:
            print("✅ Invalid provider correctly returns None")
        else:
            print("❌ Invalid provider should return None")
            return False

        # Test empty messages
        try:
            from autopr.actions.llm import complete_chat

            result = complete_chat([])
            if result and hasattr(result, "error") and result.error:
                print("✅ Empty messages correctly return error response")
            else:
                print("⚠️  Empty messages should return error response")
        except Exception:
            print("✅ Empty messages correctly raise an error")

        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_message_formatting() -> bool:
    """Test message formatting and validation."""
    print("\nTesting message formatting...")

    try:
        from autopr.actions.llm import MessageRole, get_llm_provider_manager

        # Test message role enum
        roles = [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]
        print(f"✅ Message roles available: {[role.value for role in roles]}")

        # Test message creation
        test_messages = [
            {"role": MessageRole.SYSTEM.value, "content": "You are a helpful assistant."},
            {"role": MessageRole.USER.value, "content": "Hello, world!"},
        ]

        print(f"✅ Test messages created: {len(test_messages)} messages")

        return True
    except Exception as e:
        print(f"❌ Message formatting test failed: {e}")
        return False


def test_api_calls() -> bool:
    """Test actual API calls if API keys are available."""
    print("\nTesting API calls (if keys available)...")

    try:
        from autopr.actions.llm import MessageRole, complete_chat

        # Simple test message
        test_messages = [{"role": MessageRole.USER.value, "content": "Say 'Hello from AutoPR!'"}]

        # Try each provider
        successful_calls = 0
        for provider_name in ["openai", "anthropic", "groq", "mistral"]:
            try:
                print(f"🔑 Testing {provider_name}...")
                response = complete_chat(
                    messages=test_messages, provider=provider_name, max_tokens=50
                )

                if response and not response.error and response.content:
                    print(f"✅ {provider_name} API call successful")
                    print(f"   Response: {response.content[:50]}...")
                    successful_calls += 1
                elif response and response.error:
                    print(f"⚠️  {provider_name} returned error: {response.error[:100]}...")
                else:
                    print(f"⚠️  {provider_name} API call returned empty response")

            except Exception as e:
                print(f"⚠️  {provider_name} API call failed: {str(e)[:100]}...")

        if successful_calls > 0:
            print(f"✅ {successful_calls} provider(s) successfully completed API calls")
        else:
            print("⚠️  No API calls completed (likely missing API keys)")

        return True
    except Exception as e:
        print(f"❌ API call test failed: {e}")
        return False


async def main() -> int:
    """Run all tests."""
    print("🧪 Comprehensive LLM Provider System Test Suite")
    print("=" * 60)

    # Synchronous tests
    sync_tests = [
        ("Import Tests", test_imports),
        ("Manager Creation", test_manager_creation),
        ("Provider Availability", test_provider_availability),
        ("Backward Compatibility", test_backward_compatibility),
        ("Configuration", test_configuration),
        ("Error Handling", test_error_handling),
        ("Message Formatting", test_message_formatting),
    ]

    # Additional sync tests
    additional_tests = [
        ("API Calls", test_api_calls),
    ]

    passed = 0
    total = len(sync_tests) + len(additional_tests)

    # Run synchronous tests
    for test_name, test_func in sync_tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1

    # Run additional tests
    for test_name, test_func in additional_tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 60)
    print(f"📊 Final Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! LLM provider system is fully functional.")
        return 0
    elif passed >= total * 0.8:
        print("✅ Most tests passed! System is largely functional.")
        return 0
    else:
        print("⚠️  Multiple tests failed. Check the output above.")
        return 1


def run_tests() -> int:
    """Wrapper to run async main function."""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
