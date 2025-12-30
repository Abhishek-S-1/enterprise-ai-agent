"""
Diagnostic script to check LangChain installation and find correct import paths
"""

import sys

print("=" * 60)
print("LANGCHAIN INSTALLATION DIAGNOSTICS")
print("=" * 60)

# Check Python version
print(f"\n1. Python Version: {sys.version}")

# Check installed packages
print("\n2. Checking installed packages:")
try:
    import langchain
    print(f"   ✓ langchain: {langchain.__version__}")
except ImportError as e:
    print(f"   ✗ langchain: NOT INSTALLED - {e}")

try:
    import langchain_core
    print(f"   ✓ langchain_core: {langchain_core.__version__}")
except ImportError as e:
    print(f"   ✗ langchain_core: NOT INSTALLED - {e}")

try:
    import langchain_community
    print(f"   ✓ langchain_community: {langchain_community.__version__}")
except ImportError as e:
    print(f"   ✗ langchain_community: NOT INSTALLED - {e}")

try:
    import langchain_groq
    print(f"   ✓ langchain_groq: {langchain_groq.__version__}")
except ImportError as e:
    print(f"   ✗ langchain_groq: NOT INSTALLED - {e}")

# Check for AgentExecutor in different locations
print("\n3. Checking AgentExecutor import paths:")

agent_executor_found = False

# Try path 1
try:
    from langchain.agents import AgentExecutor
    print("   ✓ Found: from langchain.agents import AgentExecutor")
    agent_executor_found = True
except ImportError:
    print("   ✗ NOT found: from langchain.agents import AgentExecutor")

# Try path 2
try:
    from langchain_core.agents import AgentExecutor
    print("   ✓ Found: from langchain_core.agents import AgentExecutor")
    agent_executor_found = True
except ImportError:
    print("   ✗ NOT found: from langchain_core.agents import AgentExecutor")

# Try path 3
try:
    from langchain.agents.agent import AgentExecutor
    print("   ✓ Found: from langchain.agents.agent import AgentExecutor")
    agent_executor_found = True
except ImportError:
    print("   ✗ NOT found: from langchain.agents.agent import AgentExecutor")

# Check for create_react_agent
print("\n4. Checking create_react_agent import paths:")

create_react_agent_found = False

# Try path 1
try:
    from langchain.agents import create_react_agent
    print("   ✓ Found: from langchain.agents import create_react_agent")
    create_react_agent_found = True
except ImportError:
    print("   ✗ NOT found: from langchain.agents import create_react_agent")

# Try path 2
try:
    from langchain.agents.react.agent import create_react_agent
    print("   ✓ Found: from langchain.agents.react.agent import create_react_agent")
    create_react_agent_found = True
except ImportError:
    print("   ✗ NOT found: from langchain.agents.react.agent import create_react_agent")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if agent_executor_found and create_react_agent_found:
    print("✅ All required imports found! Check the paths above.")
else:
    print("❌ Missing imports detected!")
    if not agent_executor_found:
        print("   - AgentExecutor not found in any location")
    if not create_react_agent_found:
        print("   - create_react_agent not found in any location")
    print("\n💡 Solution: Try reinstalling langchain packages:")
    print("   pip uninstall langchain langchain-core langchain-community -y")
    print("   pip install langchain langchain-core langchain-community")

print("\n" + "=" * 60)