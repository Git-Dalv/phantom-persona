#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys

def test_imports():
    """Test all main imports."""
    print("Testing imports...")

    # Test 1: Main client import
    print("✓ Testing: from phantom_persona import PhantomPersona, ProtectionLevel, Persona")
    from phantom_persona import PhantomPersona, ProtectionLevel, Persona
    assert PhantomPersona is not None
    assert ProtectionLevel is not None
    assert Persona is not None
    print("  ✓ Main imports OK")

    # Test 2: Proxy import
    print("✓ Testing: from phantom_persona.proxy import ProxyInfo")
    from phantom_persona.proxy import ProxyInfo
    assert ProxyInfo is not None
    print("  ✓ Proxy import OK")

    # Test 3: Config import
    print("✓ Testing: from phantom_persona.config import PhantomConfig")
    from phantom_persona.config import PhantomConfig
    assert PhantomConfig is not None
    print("  ✓ Config import OK")

    # Test 4: All persona types
    print("✓ Testing: from phantom_persona import GeoInfo, DeviceInfo, Fingerprint")
    from phantom_persona import GeoInfo, DeviceInfo, Fingerprint
    assert GeoInfo is not None
    assert DeviceInfo is not None
    assert Fingerprint is not None
    print("  ✓ Persona types OK")

    # Test 5: Core components
    print("✓ Testing: from phantom_persona import BrowserManager, ContextManager, Session")
    from phantom_persona import BrowserManager, ContextManager, Session
    assert BrowserManager is not None
    assert ContextManager is not None
    assert Session is not None
    print("  ✓ Core components OK")

    # Test 6: Exceptions
    print("✓ Testing: from phantom_persona import PhantomException, BrowserException")
    from phantom_persona import PhantomException, BrowserException
    assert PhantomException is not None
    assert BrowserException is not None
    print("  ✓ Exceptions OK")

    # Test 7: Plugins
    print("✓ Testing: from phantom_persona import Plugin, registry")
    from phantom_persona import Plugin, registry
    assert Plugin is not None
    assert registry is not None
    print("  ✓ Plugins OK")

    # Test 8: Config components
    print("✓ Testing: from phantom_persona.config import ConfigLoader, BrowserConfig")
    from phantom_persona.config import ConfigLoader, BrowserConfig
    assert ConfigLoader is not None
    assert BrowserConfig is not None
    print("  ✓ Config components OK")

    print("\n✓ All imports successful!")
    return True

if __name__ == "__main__":
    try:
        test_imports()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
